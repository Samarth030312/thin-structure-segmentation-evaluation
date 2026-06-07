# Part 2 — First Principles of Image Segmentation

## 2.1 The ladder of visual tasks

Computer vision has a ladder of tasks of increasing spatial precision. Each rung
answers a more detailed question about *where* and *what* is in an image. We climb
the ladder from the bottom.

```
  Task               Question answered                 Output
  ----------------------------------------------------------------------
  Classification     "What is in this image?"          1 label per image
  Localization       "Where is the one object?"        1 box
  Detection          "What objects, and where?"        N boxes + labels
  Semantic seg.      "What class is each pixel?"        H×W label map
  Instance seg.      "Which object owns each pixel?"    H×W + object id
  Panoptic seg.      "Both: stuff classes + things"     H×W + class + id
```

### 2.1.1 Image classification
**Question:** *What is in this image?* You feed in a picture and get one label:
"cat", "road sign", "highway". The output is a single category for the whole image.
A classifier discards all spatial information — it does not tell you *where* the cat
is. Internally, a classification network turns an `H×W×3` image into a vector of
class scores.

### 2.1.2 Localization
**Question:** *Where is the (single) object?* The output is a **bounding box** — four
numbers `(x, y, width, height)` — plus a class. Localization assumes there is one
main object to box.

### 2.1.3 Object detection
**Question:** *What objects are present and where?* Now there can be many objects.
The output is a *list* of boxes, each with a class and a confidence. Detection (YOLO,
Faster R-CNN) is the workhorse for "find the cars / pedestrians / signs". But a box
is a coarse description: a diagonal lane line inside a box is mostly *not* lane line.

### 2.1.4 Semantic segmentation — the task of this project
**Question:** *What class does each individual pixel belong to?* The output is a
**label map** of the same height and width as the image: an integer per pixel. If
there are `C` classes, the model produces, for each pixel, a length-`C` vector of
scores, and the predicted class is the arg-max.

```
   Input image (H×W×3)                 Semantic label map (H×W)
   ┌───────────────────┐               ┌───────────────────┐
   │     . ─────── .    │   model       │ 0 0 0 1 1 1 0 0 0 │   0 = background
   │   road  ┃lane┃     │  ────────►    │ 0 0 2 2 2 2 2 0 0 │   1 = lane marking
   │         ┃line┃     │               │ 0 2 2 2 2 2 2 2 0 │   2 = road
   └───────────────────┘               └───────────────────┘
```

Semantic segmentation does **not** distinguish two separate lane lines of the same
class — every "lane marking" pixel just gets label 1. That is fine for this project,
because we care about *where the markings are*, not *how many distinct ones*.

### 2.1.5 Instance segmentation
**Question:** *Which specific object instance owns each pixel?* Like semantic
segmentation, but it also separates individual objects: lane-line-1 vs lane-line-2.
Output = mask + an instance id per object. Heavier machinery (Mask R-CNN,
Mask2Former).

### 2.1.6 Panoptic segmentation
**Question:** *Both at once.* "Stuff" classes (road, sky — amorphous regions) get
semantic labels; "thing" classes (cars, signs — countable objects) get instance ids.
The single most complete description of a scene.

> **Where this project sits:** binary or multi-class **semantic segmentation** of
> thin structures (markings, narrow roads). We never need instance separation; we
> need *accurate pixel-level localisation of thin things* — and that is exactly where
> standard evaluation breaks.

## 2.2 Why segmentation exists at all

Why not just use detection boxes? Because for many real tasks the *shape* matters:

- **Lane keeping** needs the lane line's exact curve, not a box around it.
- **HD-map building** needs marking geometry to centimetre accuracy.
- **Drivable-area estimation** needs the precise road boundary.
- **Medical/material imaging** needs the exact extent of a vessel or crack.

A bounding box cannot represent a thin, curved, diagonal structure. Segmentation can,
because it labels each pixel. The price is that you now need ground-truth labels for
*every pixel* (expensive to annotate) and metrics that compare *pixel sets*.

## 2.3 Why road markings are hard

Road markings combine several difficulties that, individually, are manageable but
together are brutal:

1. **They are tiny in area.** In our real road-marking dataset (RLMD) markings occupy
   **under 2% of pixels**. The other 98%+ is background and road. A model that
   predicts "background everywhere" is ~98% pixel-accurate while being useless.

2. **Extreme class imbalance.** Across the 25 marking classes in RLMD the ratio
   between the most- and least-common class is **609:1**. Rare classes (a particular
   arrow type) may appear in a handful of images. Standard losses, left alone, ignore
   them.

3. **Thinness.** A painted line imaged from a car or drone is only a few pixels wide.
   Thin structures have a terrible **area-to-boundary ratio**: almost every pixel of
   a 3-px line is a *boundary* pixel. Any metric that punishes boundary error
   punishes thin structures everywhere. (This is the seed of the whole project.)

4. **Appearance variation.** Markings are faded, occluded by cars, wet and
   reflective, in shadow, freshly repainted, or partially erased. The *same* class
   looks wildly different.

5. **Topology matters more than area.** Operationally we care whether the line is
   *continuous and correctly placed* (can the car follow it?), which is a property of
   the centerline/topology — not whether we matched its exact painted width.

## 2.4 Why thin structures are hard — the geometric core

This deserves its own treatment because it is the heart of the monograph. Consider a
structure of width `w` pixels and length `L` pixels. Its area is `A = w·L`. Its
boundary (perimeter) is roughly `P ≈ 2L` (the two long sides; the short ends are
negligible for a long thin thing).

The **fraction of the structure that is "near the boundary"** — within one pixel of
an edge — is approximately

$$f_\text{boundary} \;\approx\; \frac{2L}{w\,L} \;=\; \frac{2}{w}.$$

- For a **wide** road, `w = 30`: only `2/30 ≈ 7%` of pixels are boundary pixels.
- For a **thin** marking, `w = 2`: `2/2 = 100%` of pixels are boundary pixels.

Every pixel of a thin structure is a boundary pixel. So **any error a model makes in
placing the boundary affects essentially the entire structure** when it is thin, but
only a thin rim of it when it is wide. Metrics that count boundary mistakes (and
area-overlap metrics implicitly do) therefore become unreliable precisely as
structures get thin. Hold this thought — Part 7 turns it into the exact law.

```
  thin (w=2): boundary IS the object        wide (w=30): boundary is a thin rim
  ┌──────────┐                              ┌────────────────────────┐
  │░░░░░░░░░░│  ░ = within 1px of edge      │░░░░░░░░░░░░░░░░░░░░░░░░│
  │░░░░░░░░░░│  (100% of the object)        │░░██████████████████░░│  ░ = rim (~7%)
  └──────────┘                              │░░██████████████████░░│  █ = interior
                                            │░░░░░░░░░░░░░░░░░░░░░░░░│
                                            └────────────────────────┘
```

## 2.5 What "ground truth" and "prediction" are, concretely

Throughout the book:

- **Ground truth (GT)** is the human-annotated label map: a 2-D array of integers,
  one per pixel. For binary tasks, `1` = foreground (marking/road), `0` = background.
- **Prediction (pred)** is the model's label map, same shape, obtained by taking the
  arg-max over class scores at each pixel.
- A **metric** is a function `metric(GT, pred) → [0,1]` summarising agreement.

Everything that follows — losses, metrics, the law — is about comparing these two
pixel arrays for thin foreground structures.

---
