"""``uavrm-validate`` - validate a dataset and emit JSON + HTML reports."""
from __future__ import annotations

import argparse
from pathlib import Path

from ..report.validator import validate_dataset, write_html, write_json
from ..utils import get_logger

log = get_logger("cli.validate")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate a segmentation dataset")
    ap.add_argument("--root", required=True)
    ap.add_argument("--num-classes", type=int, required=True)
    ap.add_argument("--ignore-index", type=int, default=None)
    ap.add_argument("--splits", nargs="*", default=["train", "val", "test"])
    ap.add_argument("--class-names", nargs="*", default=None)
    ap.add_argument("--json", default="validation_report.json")
    ap.add_argument("--html", default="validation_report.html")
    args = ap.parse_args(argv)

    report = validate_dataset(args.root, args.num_classes, tuple(args.splits),
                              args.ignore_index)
    write_json(report, args.json)
    write_html(report, args.html, class_names=args.class_names)

    log.info("Validation %s: %d errors, %d warnings -> %s / %s",
             "PASSED" if report["passed"] else "FAILED",
             report["total_errors"], report["total_warnings"], args.json, args.html)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
