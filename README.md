# OncoPlate Research · v3.0.0

**Evidence-grounded multimodal recognition and selective guidance for cancer-relevant dietary choices.**

Owner: Md Anas Biswas. Implementation of the accepted September 2026 v3.0 programme.
This repository contains executable research code and Colab notebooks. It does not contain a trained food detector, independent benchmark annotations, clinical validation, measured food chemistry, or a public-release permission.

## Start

1. Put `OncoPlate_v3_0_Colab_Research_Repo.zip` in `MyDrive/OncoPlate_Research/` and open the separately supplied `OncoPlate_Colab_Installer.ipynb` in Colab. It will not overwrite an existing checkout.
2. Run `notebooks/00_environment_and_permissions.ipynb` to verify paths, dependencies and the recorded gates. Run `90_offline_end_to_end_demo.ipynb` for an isolated CPU software check.
3. After the actual execution/data-use decisions are recorded, run **01 → 02 → 03 → 04 → 05**. The first real milestone is audited FoodNExTDB data, fixed group splits, a feature smoke test and saved seed-0 baseline predictions.
4. Run **21** for the public-data calibration/annotation-agreement study. This is not the flagship claim-support result.
5. Import the independently documented pilot/new benchmark through **06–07**, revisit **03–05** under the new dataset version, then follow the main **08–17** track. Supplemental notebooks cover VLMs, external resources, robustness, fresh cohorts, prediction sets, tuning and a local API.

Read [START_HERE](docs/START_HERE.md), the [notebook index](docs/NOTEBOOK_INDEX.md), and [data contracts](docs/DATA_CONTRACTS.md). The unchanged accepted plan is [retained here](docs/ACCEPTED_MASTER_PLAN_v3_0.md).

## What is implemented

- FoodNExTDB CSV/image schema auditing; exact hashes, reviewed near-duplicate edges and connected-component splits.
- Train-only multi-label and complete-record vocabularies; reviewer endorsement fractions and missing-field masks.
- ResNet-50, ConvNeXt-Tiny and DINOv2 ViT-S/14; frozen-feature and full-fine-tuning paths; independent and joint-record heads; seeds 0–4.
- The **60 principal predictor fits**, plus explicit separate OOF, search, calibration and VLM work.
- AMP where supported, gradient accumulation, deterministic transforms, feature shards, atomic checkpoints and interruption recovery.
- Fold-local model fitting with held groups excluded from both training and early stopping; matched logistic/MLP selectors.
- A finite source-aware claim engine, uncertainty/unknown alternatives, source conflict checks and faithful finite-template rendering.
- Shared-candidate M2/M3/M6/M7 comparisons, blind rating jobs, independent support-calibration and frozen validation thresholds.
- Documented one-action replay and matching baseline action policies; no guessed counterfactual answers.
- Hash-bound analysis locks, a separate fresh-external-cohort addendum, paired group bootstrap, seed-separated reporting and real-data user/assay analysis tools.
- Local Qwen2.5-VL/SmolVLM adapters with immutable snapshot recording; direct/staged protocols explicitly labelled adaptations.
- TorchScript/optional ONNX export, head-only int8 ablation, export parity and a local research-only API.

## Reproducibility and resources

Your Drive capacity supports persistent datasets, caches and checkpoints; it does not determine GPU VRAM or Colab local disk. Paid Colab sessions can still have variable hardware, compute-unit limits and runtime interruption. The code retains the full grid but runs selected disjoint resumable queues. See the [official Colab FAQ](https://research.google.com/colaboratory/faq.html).

Default persistent project root: `/content/drive/MyDrive/OncoPlate_Research/`.
Default local staging root: `/content/oncoplate_runtime/`.
Private research data and outputs remain **outside this public code tree**. Never auto-push a finished notebook's raw CSVs or model weights.

## Validation boundary

Release checks: **92 tests passed; 29 notebooks and 139 code cells validated; notebooks 00 and 90 executed on CPU.**


See [VALIDATION](docs/VALIDATION.md) for what was actually tested at packaging. Passing synthetic CPU checks is not a real-data or GPU training result. The original FoodNExTDB archive, DINO/VLM pretrained downloads and full GPU grid require execution in your own authorised environment.

## Scientific boundary

The retired PROTECTIVE/LOWER/MODERATE/HIGH cancer-exposure tiers are not active labels. Recognition, documentary evidence, supportability and measured chemistry remain different outcomes. Unknown does not mean safe. No first-ever priority, Q1 acceptance, clinical safety or chemical-detection result is asserted.

## Source control

The intended remote remains `anasbiswas1/oncoplate-research`, but this delivered archive has not modified it. Use a reviewed development branch and notebook 99. An existing checkout is preserved by the installer. Select a software licence with the institution before public distribution; data/checkpoint permissions are independent.
