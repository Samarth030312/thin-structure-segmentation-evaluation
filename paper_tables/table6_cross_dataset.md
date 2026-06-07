**Cross-dataset transfer (binary foreground)**

| run_name            |   mIoU |   clDice |   clRecall |   TolIoU |
|:--------------------|-------:|---------:|-----------:|---------:|
| xd_rlmd_to_rlmd     | 0.517  |   0.6343 |     0.6935 |   0.5862 |
| xd_loveda_to_loveda | 0.5083 |   0.6671 |     0.6793 |   0.5947 |
| xd_loveda_to_rlmd   | 0.0772 |   0.1314 |     0.3026 |   0.1176 |
| xd_rlmd_to_loveda   | 0.0001 |   0.4634 |     0.4634 |   0.4636 |