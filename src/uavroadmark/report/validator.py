"""Dataset validation framework.

A segmentation dataset has many silent failure modes that only surface as
mysteriously bad metrics days into a project. This validator turns them into
*loud*, up-front, machine-readable errors. Checks performed:

============================  =========================================
check                          what it catches
============================  =========================================
missing_mask / missing_image   unpaired samples (off-by-one corruption)
bad_extension                  files the loader will silently skip
corrupt_image / corrupt_mask   unreadable / truncated files
resolution_mismatch            image and mask of different H x W
empty_mask                     all-background masks (label dropout)
invalid_class_id               mask values outside ``[0, num_classes)``
duplicate_content              byte-identical images (leakage risk)
============================  =========================================

Output: a JSON report (programmatic) and an HTML report (human/visual).
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np

IMG_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MASK_EXTS = {".png", ".tif", ".tiff", ".bmp"}


@dataclass
class Issue:
    severity: str   # "error" | "warning"
    check: str
    sample: str
    detail: str


@dataclass
class SplitReport:
    split: str
    n_images: int = 0
    n_masks: int = 0
    n_paired: int = 0
    issues: List[Issue] = field(default_factory=list)
    class_pixel_counts: Dict[int, int] = field(default_factory=dict)

    def add(self, severity, check, sample, detail):
        self.issues.append(Issue(severity, check, sample, detail))

    @property
    def n_errors(self):
        return sum(i.severity == "error" for i in self.issues)

    @property
    def n_warnings(self):
        return sum(i.severity == "warning" for i in self.issues)


def _list_files(folder: Path, exts):
    good, bad = {}, []
    if not folder.is_dir():
        return good, bad
    for p in sorted(folder.iterdir()):
        if p.is_dir():
            continue
        if p.suffix.lower() in exts:
            good[p.stem] = p
        else:
            bad.append(p)
    return good, bad


def validate_split(root: Path, split: str, num_classes: int,
                   ignore_index: Optional[int] = None) -> SplitReport:
    rep = SplitReport(split=split)
    img_dir = root / "images" / split
    msk_dir = root / "masks" / split

    images, bad_img = _list_files(img_dir, IMG_EXTS)
    masks, bad_msk = _list_files(msk_dir, MASK_EXTS)
    rep.n_images, rep.n_masks = len(images), len(masks)

    for p in bad_img + bad_msk:
        rep.add("warning", "bad_extension", p.name,
                f"unexpected extension '{p.suffix}' - loader will skip it")

    for stem in sorted(set(images) - set(masks)):
        rep.add("error", "missing_mask", stem, "image has no matching mask")
    for stem in sorted(set(masks) - set(images)):
        rep.add("error", "missing_image", stem, "mask has no matching image")

    hashes = defaultdict(list)
    class_counter: Counter = Counter()
    for stem in sorted(set(images) & set(masks)):
        img_p, msk_p = images[stem], masks[stem]
        img = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
        msk = cv2.imread(str(msk_p), cv2.IMREAD_UNCHANGED)
        if img is None:
            rep.add("error", "corrupt_image", stem, f"cannot read {img_p.name}")
            continue
        if msk is None:
            rep.add("error", "corrupt_mask", stem, f"cannot read {msk_p.name}")
            continue
        if msk.ndim == 3:
            msk = msk[..., 0]
        if img.shape[:2] != msk.shape[:2]:
            rep.add("error", "resolution_mismatch", stem,
                    f"image {img.shape[:2]} vs mask {msk.shape[:2]}")

        valid = msk
        if ignore_index is not None:
            valid = msk[msk != ignore_index]
        if valid.size and int(valid.max()) >= num_classes:
            rep.add("error", "invalid_class_id", stem,
                    f"mask max id {int(valid.max())} >= num_classes {num_classes}")
        if valid.size and int(valid.min()) < 0:
            rep.add("error", "invalid_class_id", stem,
                    f"negative class id {int(valid.min())}")

        fg = msk[(msk > 0) & (msk != (ignore_index if ignore_index is not None else -999))]
        if fg.size == 0:
            rep.add("warning", "empty_mask", stem, "mask contains only background")

        for cid, cnt in zip(*np.unique(msk, return_counts=True)):
            class_counter[int(cid)] += int(cnt)

        hashes[hashlib.md5(img.tobytes()).hexdigest()].append(stem)
        rep.n_paired += 1

    for h, stems in hashes.items():
        if len(stems) > 1:
            rep.add("warning", "duplicate_content", ",".join(stems[:4]),
                    f"{len(stems)} byte-identical images (data-leakage risk)")

    rep.class_pixel_counts = dict(class_counter)
    return rep


def validate_dataset(root: str | Path, num_classes: int, splits=("train", "val", "test"),
                     ignore_index: Optional[int] = None) -> Dict:
    root = Path(root)
    reports = []
    for split in splits:
        if (root / "images" / split).is_dir():
            reports.append(validate_split(root, split, num_classes, ignore_index))
    total_errors = sum(r.n_errors for r in reports)
    total_warnings = sum(r.n_warnings for r in reports)
    return {
        "root": str(root),
        "num_classes": num_classes,
        "passed": total_errors == 0,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "splits": [
            {
                "split": r.split,
                "n_images": r.n_images,
                "n_masks": r.n_masks,
                "n_paired": r.n_paired,
                "n_errors": r.n_errors,
                "n_warnings": r.n_warnings,
                "class_pixel_counts": r.class_pixel_counts,
                "issues": [asdict(i) for i in r.issues],
            }
            for r in reports
        ],
    }


def write_json(report: Dict, path: str | Path):
    Path(path).write_text(json.dumps(report, indent=2))


_HTML_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<title>Dataset Validation Report</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:2rem;color:#222}}
h1{{margin-bottom:0}} .sub{{color:#666}}
.badge{{display:inline-block;padding:.2rem .6rem;border-radius:.4rem;color:#fff;font-weight:600}}
.pass{{background:#1a7f37}}.fail{{background:#cf222e}}
table{{border-collapse:collapse;margin:1rem 0;width:100%}}
th,td{{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;font-size:.9rem}}
th{{background:#f6f8fa}}.err{{color:#cf222e;font-weight:600}}.warn{{color:#9a6700}}
.bar{{background:#0969da;height:14px;border-radius:3px}}
</style></head><body>
<h1>Dataset Validation Report</h1>
<p class="sub">{root} &middot; {num_classes} classes &middot;
status: <span class="badge {status_class}">{status}</span>
({total_errors} errors, {total_warnings} warnings)</p>
{splits_html}
</body></html>"""


def write_html(report: Dict, path: str | Path, class_names: Optional[List[str]] = None):
    splits_html = []
    for s in report["splits"]:
        # class distribution bars
        counts = s["class_pixel_counts"]
        total = max(1, sum(counts.values()))
        rows = []
        for cid in sorted(counts, key=lambda c: int(c)):
            name = (class_names[int(cid)] if class_names and int(cid) < len(class_names)
                    else f"class {cid}")
            pct = 100 * counts[cid] / total
            rows.append(
                f"<tr><td>{cid}</td><td>{name}</td><td>{counts[cid]:,}</td>"
                f"<td>{pct:.2f}%</td>"
                f"<td><div class='bar' style='width:{max(1, pct):.1f}%'></div></td></tr>")
        dist = ("<table><tr><th>id</th><th>name</th><th>pixels</th><th>share</th>"
                "<th></th></tr>" + "".join(rows) + "</table>")

        issues = s["issues"]
        if issues:
            irows = "".join(
                f"<tr><td class='{('err' if i['severity']=='error' else 'warn')}'>"
                f"{i['severity']}</td><td>{i['check']}</td><td>{i['sample']}</td>"
                f"<td>{i['detail']}</td></tr>" for i in issues[:200])
            itable = ("<table><tr><th>severity</th><th>check</th><th>sample</th>"
                      "<th>detail</th></tr>" + irows + "</table>")
        else:
            itable = "<p>No issues 🎉</p>"

        splits_html.append(
            f"<h2>Split: {s['split']}</h2>"
            f"<p>{s['n_images']} images, {s['n_masks']} masks, "
            f"{s['n_paired']} paired &middot; "
            f"<span class='err'>{s['n_errors']} errors</span>, "
            f"<span class='warn'>{s['n_warnings']} warnings</span></p>"
            f"<h3>Class pixel distribution</h3>{dist}"
            f"<h3>Issues</h3>{itable}")

    html = _HTML_TEMPLATE.format(
        root=report["root"], num_classes=report["num_classes"],
        status="PASS" if report["passed"] else "FAIL",
        status_class="pass" if report["passed"] else "fail",
        total_errors=report["total_errors"], total_warnings=report["total_warnings"],
        splits_html="".join(splits_html))
    Path(path).write_text(html)
