#!/usr/bin/env python3
"""Regenerate a live hardware/software snapshot for reports/system_report.md."""
import platform
import shutil
import subprocess


def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "n/a"


def main():
    cpu = sh("lscpu | grep 'Model name' | head -1 | cut -d: -f2").strip()
    threads = sh("nproc")
    ram = sh("free -h | awk '/Mem:/ {print $2}'")
    disk = sh("df -h /home | tail -1 | awk '{print $4}'")
    print("# Live System Snapshot\n")
    print(f"- Platform: {platform.platform()}")
    print(f"- CPU: {cpu}  ({threads} threads)")
    print(f"- RAM: {ram}")
    print(f"- Disk free: {disk}")
    print(f"- GPU: {sh('nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader')}")
    try:
        import torch
        print(f"- torch: {torch.__version__} | cuda build {torch.version.cuda} | "
              f"available={torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"- GPU (torch): {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("- torch: not installed")
    for pkg in ("segmentation_models_pytorch", "tensorboard"):
        v = sh(f"python3 -c 'import {pkg}; print({pkg}.__version__)'")
        print(f"- {pkg}: {v}")


if __name__ == "__main__":
    main()
