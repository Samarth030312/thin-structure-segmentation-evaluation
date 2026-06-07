#!/usr/bin/env python3
"""Extract paper-ready tables (markdown + LaTeX) from result files into
paper_tables/. Re-runnable; skips a table if its source is missing."""
import json
import os

import pandas as pd

OUT = "paper_tables"
os.makedirs(OUT, exist_ok=True)


def emit(df, name, caption):
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    with open(f"{OUT}/{name}.md", "w") as f:
        f.write(f"**{caption}**\n\n")
        try:
            f.write(df.to_markdown(index=False))
        except ImportError:
            f.write(df.to_string(index=False))
    try:
        with open(f"{OUT}/{name}.tex", "w") as f:
            f.write(df.to_latex(index=False, caption=caption, float_format="%.3f"))
    except Exception:
        pass
    print(f"  {OUT}/{name}.{{csv,md,tex}}")


def t_loss_ablation():
    if not os.path.exists("reports/leaderboard.csv"):
        return
    df = pd.read_csv("reports/leaderboard.csv")
    losses = ["ce", "dice", "ce_dice", "focal", "tversky", "core"]
    r = df[df.run_name.isin([f"rlmd_unetpp_{l}" for l in losses])].copy()
    if r.empty:
        return
    r["loss"] = r.run_name.str.replace("rlmd_unetpp_", "")
    r = r[["loss", "mIoU", "PixelAcc", "clDice", "clRecall", "TolIoU"]]
    r["ord"] = r["loss"].map({l: i for i, l in enumerate(losses)})
    r = r.sort_values("ord").drop(columns="ord")
    emit(r, "table2_rlmd_loss_ablation", "RLMD clean 6-loss ablation (U-Net++)")


def t_arch():
    if not os.path.exists("reports/leaderboard.csv"):
        return
    df = pd.read_csv("reports/leaderboard.csv")
    r = df[df.run_name.str.startswith("arch_")].copy()
    if r.empty:
        return
    r["model"] = r.run_name.str.replace("arch_", "")
    r = r[["model", "mIoU", "clDice", "BoundaryIoU", "params_M"]]
    emit(r, "table3_arch_sweep", "Architecture sweep (synthetic)")


def t_perf():
    if os.path.exists("reports/leaderboard_performance.csv"):
        emit(pd.read_csv("reports/leaderboard_performance.csv"),
             "table4_performance", "Performance / deployment metrics")


def t_xdomain():
    if os.path.exists("reports/leaderboard_xdomain.csv"):
        df = pd.read_csv("reports/leaderboard_xdomain.csv")
        emit(df[["run_name", "mIoU", "clDice", "clRecall", "TolIoU"]],
             "table6_cross_dataset", "Cross-dataset transfer (binary foreground)")


def t_multiseed():
    p = "reports/multiseed_results.json"
    if os.path.exists(p):
        d = json.load(open(p))
        rows = [{"loss": k, **v} for k, v in d.items()]
        emit(pd.DataFrame(rows), "table7_multiseed", "Multi-seed CIs (headline)")


if __name__ == "__main__":
    print("Extracting paper tables...")
    t_loss_ablation(); t_arch(); t_perf(); t_xdomain(); t_multiseed()
    print("Done ->", OUT)
