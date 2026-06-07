# Performance Profiling & Bottleneck Analysis

> Systems-level analysis of the training pipeline on the GTX-1650, via
> `scripts/run_profiling.py` (torch.profiler op breakdown + dataloader-throughput
> sweep). Raw: `reports/profiling/profiler_top_ops.txt`, `profiling_summary.json`.

## 1. Data pipeline throughput (CPU side)

| num_workers | imgs/s |
|---|---|
| 0 | 61.6 |
| 2 | 67.4 |
| 6 | **71.7** |

The dataloader sustains **~72 imgs/s** with 6 workers (decode 512² PNG +
albumentations resize/normalise). Multi-worker prefetch + pinned memory are
enabled in the trainer; the gain from 0→6 workers is modest (+16 %), indicating
the input pipeline is **not** the bottleneck at this batch size.

## 2. Where the time goes (GPU side)

torch.profiler over 10 training steps (U-Net R34, 384², fp32):

| Op | Share of CUDA time |
|---|---|
| `convolution_backward` | **42.7 %** |
| cuDNN winograd conv (fwd) | 25.7 % |
| `cudnn_convolution` (fwd) | 17.0 % |
| `cudnn_batch_norm_backward` | 5.4 % |
| elementwise (`mul`, etc.) | 4.5 % |

**Convolutions dominate ~85 % of GPU time** — the expected profile for a CNN
segmenter. BatchNorm and elementwise ops are minor.

## 3. Bottleneck diagnosis

- **Training is GPU-compute-bound, not data-bound.** The data pipeline supplies
  ~72 imgs/s, but training proceeds at ~5 imgs/s (96 s / 500 imgs / epoch) — the
  GPU is the limiter by ~14×. Adding more dataloader workers would *not* speed up
  training; the 4 GB GTX-1650's conv throughput is the wall.
- **Implication for optimisation:** the levers that matter here are (a) **mixed
  precision** (fp16 conv on tensor-core GPUs — note: the 1650 lacks tensor cores
  and fp16 *diverged* for from-scratch training, so we run fp32), (b) **lighter
  backbones / fewer FLOPs** (SegFormer-B0 has 6× fewer GFLOPs than U-Net — see
  `leaderboard_performance.csv`), (c) **TensorRT/ONNX** at inference. Tuning the
  CPU pipeline would be wasted effort given the diagnosis.

## 4. Memory

Measured peak VRAM (training, batch 4, 384²): U-Net ~3.0 GB, U-Net++ ~3.6 GB
(OOM at batch 8 → batch 4 + grad-accum 2). Inference peak (batch 1, 512²) is far
lower (0.2-0.4 GB, `leaderboard_performance.csv`) — training activations, not
weights, are the memory driver, which is why gradient accumulation (not a smaller
model) is the right knob to fit larger effective batches.

## 5. Engineering optimisations applied

- multi-worker dataloaders + `pin_memory` + non-blocking H2D copies,
- gradient accumulation (decouple effective batch from VRAM),
- fp32 loss under AMP (numerical stability) with AMP autocast for the forward,
- `expandable_segments` allocator to avoid fragmentation OOM,
- deterministic seeding for reproducible throughput/accuracy.

## 6. Takeaway for an AV training cluster

On real hardware (A100/H100 with tensor cores), the same code path flips to
**data-bound** at large batch — at which point the dataloader-worker sweep and
`pin_memory` (already in place) become the relevant levers, and AMP delivers its
full speedup (fp16 is stable on tensor-core GPUs with pretrained encoders). The
profiling harness is the tool to re-diagnose on the target hardware.
