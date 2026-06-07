# Benchmark Leaderboard (auto-generated; real RLMD + synthetic GPU runs)

> rlmd_* = REAL primary evidence. Note: mIoU ranks rlmd_unetpp_tversky #1 but PixelAcc 0.009 (floods frame) - see real_data_results.md.

| run_name | model | loss | split | mIoU | mDice | mF1 | mPrecision | mRecall | PixelAcc | FWIoU | clDice | BoundaryIoU | clF1 | clRecall | TolIoU | params_M | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abl_unet_core | unet | core | test | 0.9453 | 0.9716 | 0.9716 | 0.9791 | 0.9646 | 0.9987 | 0.9974 | 0.9993 | 0.9859 | 1.0 | 1.0 | 0.9948 | 24.44 | loss ablation: core |
| abl_unet_ce_dice | unet | ce_dice | test | 0.9378 | 0.9675 | 0.9675 | 0.9744 | 0.9613 | 0.9985 | 0.9971 | 0.9979 | 0.9857 | 1.0 | 1.0 | 0.9941 | 24.44 | loss ablation: ce_dice |
| arch_unetpp | unetpp | ce_dice | test | 0.9327 | 0.9645 | 0.9645 | 0.9718 | 0.9584 | 0.9986 | 0.9972 | 0.9993 | 0.9869 | 1.0 | 1.0 | 0.995 | 26.08 | architecture sweep: unetpp (ce_dice) |
| arch_deeplabv3plus | deeplabv3plus | ce_dice | test | 0.8782 | 0.9348 | 0.9348 | 0.9305 | 0.9396 | 0.9945 | 0.9894 | 0.9946 | 0.8981 | 1.0 | 0.9999 | 0.9462 | 26.68 | architecture sweep: deeplabv3plus (ce_dice) |
| arch_segformer | segformer | ce_dice | test | 0.8471 | 0.9154 | 0.9154 | 0.9217 | 0.91 | 0.9948 | 0.9901 | 0.9965 | 0.9181 | 0.9997 | 0.9994 | 0.9589 | 3.72 | architecture sweep: segformer (ce_dice) |
| abl_unet_tversky | unet | tversky | test | 0.7874 | 0.8101 | 0.8101 | 0.7992 | 0.9571 | 0.5123 | 0.5093 | 0.2194 | 0.0546 | 0.4266 | 1.0 | 0.209 | 24.44 | loss ablation: tversky |
| arch_pspnet | pspnet | ce_dice | test | 0.6345 | 0.7747 | 0.7747 | 0.7392 | 0.8203 | 0.9768 | 0.9601 | 0.9187 | 0.6199 | 0.9916 | 0.9952 | 0.7857 | 21.47 | architecture sweep: pspnet (ce_dice) |
| rlmd_unetpp_tversky | unetpp | tversky | test | 0.144 | 0.2079 | 0.2079 | 0.189 | 0.2579 | 0.0091 | 0.0058 | 0.0836 | 0.0733 | 0.2277 | 1.0 | 0.0437 | 26.08 | RLMD clean loss ablation: unetpp+tversky (fp32 384 pretrained, 500-img subset) |
| abl_unet_cldice | unet | cldice | test | 0.0323 | 0.0546 | 0.0546 | 0.0395 | 0.1613 | 0.1109 | 0.1026 | 0.45 | 0.2911 | 0.4908 | 0.9999 | 0.1019 | 24.44 | loss ablation: cldice |
| rlmd_unetpp_ce_dice | unetpp | ce_dice | test | 0.0286 | 0.0425 | 0.0425 | 0.118 | 0.0458 | 0.9833 | 0.9692 | 0.3728 | 0.2413 | 0.4887 | 0.3559 | 0.3244 | 26.08 | RLMD clean loss ablation: unetpp+ce_dice (fp32 384 pretrained, 500-img subset) |
| rlmd_unet_ce_dice | unet | ce_dice | test | 0.0122 | 0.0189 | 0.0189 | 0.0166 | 0.0227 | 0.9819 | 0.9665 | 0.0916 | 0.0663 | 0.1347 | 0.0955 | 0.0911 | 24.44 | RLMD real road markings: unet+ce_dice (fp32 384 pretrained, 500-img subset) |
| rlmd_unetpp_core | unetpp | core | test | 0.0052 | 0.0093 | 0.0093 | 0.0072 | 0.0133 | 0.9805 | 0.9647 | 0.2751 | 0.1926 | 0.3214 | 0.2106 | 0.2151 | 26.08 | RLMD real road markings: unetpp+core (fp32 384 pretrained, 500-img subset) |
