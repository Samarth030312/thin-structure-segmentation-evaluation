# When mIoU Lies

## A Master Monograph on Thin-Structure Segmentation, Evaluation Metrics, and the Width-Coupling Law

*A self-contained technical textbook for the UAV / road-marking segmentation research project.*

---

**How to read this book.** This monograph teaches the entire project from first
principles. It assumes you are a competent programmer with a moderate mathematics
background (you remember what a derivative and a matrix are) but little research
experience. Every concept — convolution, backpropagation, IoU, clDice, U-Net,
skeletonisation — is built up from fundamentals, with (1) intuition, (2) a
derivation, (3) a small numerical example, and (4) why it matters for *this*
project. By the end you should be able to **reproduce, defend, teach, and extend**
the work without opening any other file.

**The one-sentence thesis.** The standard segmentation metric, mean Intersection-
over-Union (mIoU), *systematically and predictably under-reports the quality of thin
structures* (road markings, lane lines, narrow roads) that a model has in fact
correctly detected — and the size of that error obeys a simple geometric law,
`Gap(w) = clDice − mIoU ≈ 2δ/(w+2δ)`, where `w` is the structure's width in pixels
and `δ` is the model's boundary-localisation error.

**A note on honesty.** This project is as much about *scientific discipline* as
about results. You will find documented negative results (a loss that did not work;
a dataset whose roads were too wide to show the effect), an honestly unreachable
dataset (SkyScapes), and explicit statements of where the central law breaks. That
candour is deliberate and is part of what the monograph teaches.

---

### Table of contents

1. Executive overview — the whole project in plain English
2. First principles of image segmentation
3. Mathematical foundations (vectors → losses → metrics)
4. Computer-vision architectures (U-Net, U-Net++, DeepLabV3+, PSPNet, SegFormer)
5. Datasets (synthetic, RLMD, LoveDA, MassRoads, UAVid)
6. Experimental design
7. **The width-coupling theory** (the intellectual centre)
8. Results — every figure, table, and experiment
9. Reviewer-defense guide (100 questions and answers)
10. Code walkthrough
11. Engineering & system design
12. Future research
13. Personal-mastery checklist (100 questions + answer key)

---
