# Citation Checklist

Essential references (BibTeX keys to add). Verify DOIs/venues at submission.

## Architectures
- [ ] Ronneberger et al., *U-Net*, MICCAI 2015.
- [ ] Zhou et al., *UNet++*, DLMIA 2018.
- [ ] Chen et al., *DeepLabV3+*, ECCV 2018.
- [ ] Zhao et al., *PSPNet*, CVPR 2017.
- [ ] Xie et al., *SegFormer*, NeurIPS 2021.
- [ ] (mentioned) Wang et al., *HRNet*, TPAMI 2020; Cheng et al., *Mask2Former*, CVPR 2022.

## Thin-structure metrics & losses (core to our contribution)
- [ ] Shit et al., *clDice + soft-skeleton*, CVPR 2021.  ← method basis for CoRe
- [ ] Cheng et al., *Boundary IoU*, CVPR 2021.
- [ ] Milletari et al., *V-Net / Dice*, 3DV 2016.
- [ ] Lin et al., *Focal Loss*, ICCV 2017.
- [ ] Salehi et al., *Tversky loss*, MLMI 2017.
- [ ] Selvaraju et al., *Grad-CAM*, ICCV 2017.

## Datasets
- [ ] RLMD — *RLMD: A Dataset for Road Marking Segmentation*, IEEE (doi 10226935). ← primary
- [ ] Wang et al., *LoveDA*, NeurIPS D&B 2021. ← cross-dataset
- [ ] Azimi et al., *SkyScapes*, ICCV 2019; *Aerial-LaneNet*, TGRS 2019.
- [ ] Varma et al., *IDD*, WACV 2019; Jayasinghe et al., *CeyMo*, WACV 2022.
- [ ] Lyu et al., *UAVid*, ISPRS 2020.

## Deployment / systems
- [ ] ONNX Runtime; NVIDIA TensorRT (cite docs/whitepaper).
- [ ] Kirillov et al., *Segment Anything*, ICCV 2023; Zhang et al., *MobileSAM*, 2023 (foundation-model study).

## To verify before submission
- [ ] RLMD exact IEEE citation (authors, title, year, doi 10.1109/...10226935).
- [ ] LoveDA license terms for the HF mirror (`chloechia/loveda`).
- [ ] clDice attribution is prominent (our CoRe builds directly on it).
