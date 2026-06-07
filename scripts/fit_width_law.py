#!/usr/bin/env python3
"""Fit candidate functional forms to Gap(width) from the controlled study and the
real datasets. Compare by R^2 and AIC; the first-principles inverse-width form
Gap = 2d/(w+2d) is among the candidates."""
import json
import os
import sys

import numpy as np
from scipy.optimize import curve_fit

OUT = "reports/controlled"


def forms():
    return {
        "inverse (2d/(w+2d))": (lambda w, d: 2 * d / (w + 2 * d), [1.0]),
        "rational (a/(w+b))": (lambda w, a, b: a / (w + b), [1.0, 1.0]),
        "power (a*w^-k)": (lambda w, a, k: a * np.power(w, -k), [1.0, 1.0]),
        "exp (a*exp(-w/t))": (lambda w, a, t: a * np.exp(-w / t), [0.6, 5.0]),
        "log (a-b*log w)": (lambda w, a, b: a - b * np.log(w), [0.6, 0.2]),
        "linear (a-b*w)": (lambda w, a, b: a - b * w, [0.5, 0.02]),
    }


def fit_report(w, gap):
    w = np.asarray(w, float); gap = np.asarray(gap, float)
    n = len(w); res = {}
    for name, (f, p0) in forms().items():
        try:
            popt, _ = curve_fit(f, w, gap, p0=p0, maxfev=20000)
            pred = f(w, *popt)
            ss_res = float(np.sum((gap - pred) ** 2))
            ss_tot = float(np.sum((gap - gap.mean()) ** 2))
            r2 = 1 - ss_res / ss_tot
            k = len(popt)
            aic = n * np.log(ss_res / n + 1e-12) + 2 * k
            res[name] = {"params": [round(float(x), 4) for x in popt],
                         "R2": round(r2, 4), "AIC": round(aic, 2), "k": k}
        except Exception as e:  # noqa: BLE001
            res[name] = {"error": str(e)}
    return res


def main():
    data = json.load(open(os.path.join(OUT, "robustness_sweeps.json")))
    prim = data["dilate_1"]
    w = [r["width"] for r in prim]; gap = [r["gap"] for r in prim]

    print("=== Fit to controlled data (dilate_1, 13 widths) ===")
    res = fit_report(w, gap)
    ranked = sorted([(v.get("AIC", 1e9), k, v) for k, v in res.items()])
    for aic, name, v in ranked:
        if "error" in v:
            print(f"  {name:22s} FAILED"); continue
        print(f"  {name:22s} R2={v['R2']:.4f}  AIC={v['AIC']:8.2f}  params={v['params']}")
    best = ranked[0][1]
    print(f"\nBest by AIC: {best}")

    # real datasets on the same curve
    real = [("Synthetic", 2.0, 0.65), ("MassRoads", 4.0, 0.265),
            ("LoveDA", 5.0, 0.22), ("UAVid", 20.0, 0.007)]
    inv = forms()["inverse (2d/(w+2d))"][0]
    d = res["inverse (2d/(w+2d))"]["params"][0]
    print(f"\n=== Real datasets vs inverse law (d={d}) ===")
    for name, ww, g in real:
        print(f"  {name:10s} w={ww:5.1f}  observed gap={g:+.3f}  "
              f"law={inv(ww, d):+.3f}  resid={g-inv(ww,d):+.3f}")

    json.dump({"controlled_fit": res, "best_by_aic": best,
               "inverse_d": d, "real_points": real},
              open(os.path.join(OUT, "law_fit.json"), "w"), indent=2)
    print(f"\nWrote {OUT}/law_fit.json")


if __name__ == "__main__":
    main()
