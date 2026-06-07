#!/usr/bin/env python3
"""Export a trained checkpoint to TorchScript (+ optional ONNX) for deployment.

The C++/LibTorch inference engine (`deploy/cpp/`) consumes the TorchScript file;
ONNX feeds TensorRT for on-board UAV inference. We **trace** (not script) because
smp models contain control flow that scripting rejects; tracing is sufficient for
a fixed-shape segmentation forward pass.

    python scripts/export_model.py \
        --config configs/experiment/abl_unet_core.yaml \
        --checkpoint outputs/abl_unet_core/best.pth \
        --out deploy/models/unet_core --size 256 --onnx
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.utils import load_config  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--out", required=True, help="output path prefix (no extension)")
    ap.add_argument("--size", type=int, default=256)
    ap.add_argument("--onnx", action="store_true")
    args = ap.parse_args()

    import torch

    cfg = load_config(args.config)
    model = build_model_from_cfg(cfg)
    ckpt = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(ckpt["model"] if "model" in ckpt else ckpt)
    model.eval()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    example = torch.randn(1, 3, args.size, args.size)

    # --- TorchScript (traced) ---
    with torch.no_grad():
        traced = torch.jit.trace(model, example)
    ts_path = f"{args.out}.ts.pt"
    traced.save(ts_path)
    # sanity: reload and compare
    reloaded = torch.jit.load(ts_path)
    with torch.no_grad():
        a = model(example); b = reloaded(example)
    max_diff = (a - b).abs().max().item()
    print(f"[TorchScript] saved {ts_path}  (reload max|Δ|={max_diff:.2e})")

    # metadata for the C++ side
    meta = {
        "num_classes": int(cfg["dataset"]["num_classes"]),
        "size": args.size,
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "class_names": cfg["dataset"].get("class_names"),
    }
    import json
    with open(f"{args.out}.meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[meta] saved {args.out}.meta.json")

    # --- ONNX (optional, for TensorRT) ---
    if args.onnx:
        onnx_path = f"{args.out}.onnx"
        torch.onnx.export(
            model, example, onnx_path, opset_version=17,
            input_names=["input"], output_names=["logits"],
            dynamic_axes={"input": {0: "batch", 2: "h", 3: "w"},
                          "logits": {0: "batch", 2: "h", 3: "w"}})
        print(f"[ONNX] saved {onnx_path}")


if __name__ == "__main__":
    main()
