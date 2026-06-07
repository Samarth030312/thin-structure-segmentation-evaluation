// Real-time UAV road-marking segmentation — C++/LibTorch inference engine.
//
// Loads a TorchScript model exported by scripts/export_model.py and runs a
// single forward pass over an input image, producing a colourised mask + an
// overlay. This is the deployment artifact for on-board UAV inference; the same
// TorchScript graph also feeds a TensorRT path on Jetson-class hardware.
//
// Build: see deploy/cpp/CMakeLists.txt (requires LibTorch + OpenCV).
// Usage: ./uavrm_infer <model.ts.pt> <image> <out_overlay.png> [size]
//
// Design notes for reviewers:
//  * Preprocessing mirrors the Python eval transform exactly (resize ->
//    ImageNet normalise -> CHW float) so train/deploy parity holds.
//  * argmax is done on-device; only the final label map is copied to host.
//  * Timing is reported to expose the accuracy/latency trade-off AV teams care
//    about.

#include <torch/script.h>
#include <opencv2/opencv.hpp>

#include <chrono>
#include <iostream>
#include <vector>

namespace {

// 7-class road-marking palette (BGR), matching uavroadmark.data.synthetic.
const std::vector<cv::Vec3b> kPalette = {
    {0, 0, 0},       // background
    {220, 220, 220}, // solid_lane_line
    {255, 255, 0},   // dashed_lane_line
    {255, 0, 255},   // zebra_crossing
    {0, 128, 255},   // road_arrow
    {0, 0, 255},     // stop_line
    {0, 255, 255},   // yellow_line
};
const float kMean[3] = {0.485f, 0.456f, 0.406f}; // RGB
const float kStd[3]  = {0.229f, 0.224f, 0.225f};

// HWC BGR uint8 -> 1x3xHxW float tensor, RGB, ImageNet-normalised.
torch::Tensor preprocess(const cv::Mat& bgr, int size) {
  cv::Mat resized, rgb;
  cv::resize(bgr, resized, cv::Size(size, size));
  cv::cvtColor(resized, rgb, cv::COLOR_BGR2RGB);
  rgb.convertTo(rgb, CV_32F, 1.0 / 255.0);

  auto tensor = torch::from_blob(rgb.data, {size, size, 3}, torch::kFloat32).clone();
  tensor = tensor.permute({2, 0, 1}); // HWC -> CHW
  for (int c = 0; c < 3; ++c) {
    tensor[c] = tensor[c].sub_(kMean[c]).div_(kStd[c]);
  }
  return tensor.unsqueeze(0); // 1x3xHxW
}

cv::Mat colourise(const cv::Mat& label_map) {
  cv::Mat colour(label_map.size(), CV_8UC3);
  for (int y = 0; y < label_map.rows; ++y) {
    for (int x = 0; x < label_map.cols; ++x) {
      int id = label_map.at<uchar>(y, x);
      colour.at<cv::Vec3b>(y, x) =
          (id >= 0 && id < static_cast<int>(kPalette.size())) ? kPalette[id]
                                                              : cv::Vec3b{0, 0, 0};
    }
  }
  return colour;
}

} // namespace

int main(int argc, const char* argv[]) {
  if (argc < 4) {
    std::cerr << "Usage: " << argv[0]
              << " <model.ts.pt> <image> <out_overlay.png> [size=256]\n";
    return 1;
  }
  const std::string model_path = argv[1];
  const std::string image_path = argv[2];
  const std::string out_path = argv[3];
  const int size = (argc > 4) ? std::stoi(argv[4]) : 256;

  torch::jit::script::Module model;
  try {
    model = torch::jit::load(model_path);
  } catch (const c10::Error& e) {
    std::cerr << "Failed to load model: " << e.what() << "\n";
    return 1;
  }
  torch::Device device(torch::cuda::is_available() ? torch::kCUDA : torch::kCPU);
  model.to(device);
  model.eval();
  torch::NoGradGuard no_grad;

  cv::Mat image = cv::imread(image_path, cv::IMREAD_COLOR);
  if (image.empty()) {
    std::cerr << "Failed to read image: " << image_path << "\n";
    return 1;
  }

  auto input = preprocess(image, size).to(device);

  auto t0 = std::chrono::high_resolution_clock::now();
  auto logits = model.forward({input}).toTensor();      // 1xCxHxW
  auto pred = logits.argmax(1).squeeze(0).to(torch::kU8).cpu(); // HxW
  auto t1 = std::chrono::high_resolution_clock::now();
  double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

  cv::Mat label_map(size, size, CV_8UC1, pred.data_ptr<uchar>());
  cv::Mat colour = colourise(label_map.clone());

  // overlay on the (resized) input
  cv::Mat resized;
  cv::resize(image, resized, cv::Size(size, size));
  cv::Mat overlay;
  cv::addWeighted(resized, 0.6, colour, 0.4, 0.0, overlay);
  cv::imwrite(out_path, overlay);

  std::cout << "device=" << (device.is_cuda() ? "cuda" : "cpu")
            << "  inference=" << ms << " ms"
            << "  (" << 1000.0 / ms << " FPS)"
            << "  -> " << out_path << "\n";
  return 0;
}
