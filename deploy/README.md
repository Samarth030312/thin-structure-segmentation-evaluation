# Deployment — C++/LibTorch + TensorRT inference

Real-time, on-board UAV road-marking segmentation. The research/training stack is
Python; **deployment is C++** for predictable latency and easy integration into
an embedded flight/perception stack (Jetson Orin/Xavier class).

## Pipeline

```
 PyTorch checkpoint ──scripts/export_model.py──► TorchScript (.ts.pt)  ─► LibTorch C++  (deploy/cpp)
                                              └► ONNX (.onnx)          ─► TensorRT engine (Jetson)
```

## 1. Export from Python

```bash
python scripts/export_model.py \
    --config configs/experiment/abl_unet_core.yaml \
    --checkpoint outputs/abl_unet_core/best.pth \
    --out deploy/models/unet_core --size 256 --onnx
# -> deploy/models/unet_core.ts.pt   (TorchScript, verified reload)
#    deploy/models/unet_core.meta.json
#    deploy/models/unet_core.onnx     (for TensorRT)
```

## 2. Build the C++ engine

Requires [LibTorch](https://pytorch.org/get-started/locally/) (download the
C++/Java distribution matching your CUDA) and OpenCV.

```bash
cd deploy/cpp
mkdir build && cd build
cmake -DCMAKE_PREFIX_PATH="/path/to/libtorch" ..
cmake --build . --config Release -j
```

## 3. Run

```bash
./uavrm_infer ../../models/unet_core.ts.pt input.png overlay.png 256
# device=cuda  inference=12.4 ms  (80.6 FPS)  -> overlay.png
```

The C++ preprocessing (resize → RGB → ImageNet-normalise → CHW) **mirrors the
Python eval transform exactly**, guaranteeing train/deploy parity; argmax runs
on-device and only the label map is copied to host.

## 4. TensorRT path (Jetson)

```bash
trtexec --onnx=deploy/models/unet_core.onnx \
        --saveEngine=unet_core_fp16.engine --fp16
```
INT8 calibration with a few hundred representative frames typically halves
latency again; the dynamic axes in the ONNX export allow variable input
resolution for different UAV altitudes.

## Notes

- LibTorch is a multi-GB download and is **not** vendored here; the C++ sources
  compile against it. The export script and TorchScript reload are verified in
  Python (`scripts/export_model.py` checks `max|Δ|` between eager and scripted
  outputs).
- For lowest latency pick an efficient model (SegFormer-B0, U-Net-R18) and
  report FPS alongside accuracy on the leaderboard — deployment is a Pareto
  decision, not an accuracy-only one.
