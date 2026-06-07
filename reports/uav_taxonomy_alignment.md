# UAV Taxonomy Alignment

The acquired datasets have disjoint class sets, so a common taxonomy is required.
Because (a) only the *road* class is shared and meaningful for the thin-structure
question, and (b) marking sub-classes are unavailable in the free UAV data, we
align to a **binary road / background** taxonomy.

## 1. Common taxonomy

| id | class |
|---|---|
| 0 | background (everything else) |
| 1 | road (drivable road surface) |

## 2. Mapping per dataset

| Source dataset | Source classes | → target |
|---|---|---|
| **UAVid** | background, building, road `(128,64,128)`, tree, low-veg, moving-car, static-car, human | road → 1; all others → 0 |
| **LoveDA** | background, building, road `(id 3)`, water, barren, forest, agriculture | road → 1; all others → 0 |
| RLMD (ground, reference) | 25 marking classes | any marking → 1 (binary marking, separate experiment) |

## 3. What was merged / removed, and why

- **Merged into background (0):** all non-road classes (buildings, vegetation,
  vehicles, water, etc.). *Why:* they are not the structure under study and differ
  entirely between datasets; merging yields a clean, shared binary task.
- **Removed:** nothing was discarded silently — every source pixel maps to either
  road or background. Void/no-data pixels (if any) map to `ignore_index=255`.
- **Not aligned across viewpoints:** we deliberately do **not** claim cross-dataset
  *transfer* here (ground markings vs aerial roads are different structures); each
  dataset is trained and evaluated *within itself*. The shared taxonomy exists so
  the **same metrics and the same width-stratified analysis** apply to each.

## 4. Rationale for binary (not the 7-class example taxonomy)

The campaign's example taxonomy (background/road/lane-marking/crosswalk/arrow/
stop-line/other) cannot be populated: **no free UAV dataset provides aerial
*marking* sub-classes** (`uav_dataset_survey.md`). Forcing those classes onto
road-surface data would fabricate labels. The honest, evidence-preserving choice
is **binary road**, which (i) is genuinely shared, (ii) supports the
thin-structure question (thin vs wide road segments), and (iii) requires no
invented annotations. The richer taxonomy is recoverable on SkyScapes (ingestion
built) as future work.
