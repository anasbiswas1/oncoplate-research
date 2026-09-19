# Start experimenting

## Installation

Download the repository ZIP and standalone installer notebook supplied with this release. Upload the ZIP to `MyDrive/OncoPlate_Research/`. In Colab choose **File → Upload notebook**, select the installer, and run its cells. The installer verifies the ZIP checksum, rejects unsafe archive paths, and installs into `oncoplate-research` when vacant. When that directory already contains a checkout, it uses a new versioned sibling instead and records the actual location in `.oncoplate_install.json`. Existing files and Git history are not overwritten.

Open notebooks using Colab's Google Drive picker. They read the installation pointer. Local users may set `ONCOPLATE_REPO` and `ONCOPLATE_DRIVE_ROOT`.

## First session

Use notebook **00**. It initialises persistent folders, records Python/package/GPU details, preserves Colab's torch/torchvision installation, and runs tests. Each runtime should repeat its dependency/environment check. For DINO/VLM runs use the optional installation in **18** or install `transformers==4.57.1`, `accelerate`, and `huggingface-hub` without replacing torch.

Use **90** for a full CPU software demonstration. Artificial colour arrays are generated in `software_checks/<timestamp>/DEMO_ONLY`; nothing enters the actual research dataset. The demonstration tests a miniature encoder and selectors, not food recognition.

## Execution decisions

`governance/approvals.json` begins pending. Fill genuine decision references, decision-maker and dates where the existing programme requires them. The project owner's acceptance is already recorded; these are not requests to accept the scope again. Never invent a supervisor or ethics approval just to clear a software gate. Offline synthetic testing remains available.

For FoodNExTDB, the execution and research-use terms gates are relevant. New collection, domain claims, user evaluation, optional assays and public release have separate gates. A notebook cannot obtain those decisions for you.

## First real experiment

Run **01**: retain the downloaded source ZIP in Drive and stage it locally. The adapter verifies names, schema, image readability and annotation pairing. The complete archive was not available in the packaging environment. A schema mismatch stops with a diagnostic rather than guessing the missing relationships.

Run **02**: inspect fields and target definitions. Run **03**: complete the near-duplicate review, enter its real reference, freeze groups and build train-only labels. Run **04**: 256-image ResNet feature check. Run **05**: frequency and two seed-0 learned baselines.

At this point inspect the audit, target specification, split integrity, smoke result, training histories, saved validation logits and per-label results. Do not jump directly to a 60-run launch with an unverified parser.

Run **21** to calibrate and evaluate public visual annotation agreement under a separate lock. Those outputs must not be labelled cancer-food identification accuracy.

## Main benchmark

The independently documented benchmark has its own dataset version and paths. Use **06** for real pilot analysis and **07** to import actual reviewed JSONL records, annotations, inference states and claim rules. Notebook 07 changes the active dataset pointer without deleting the foundation. Re-run **03–05** on the new dataset, then follow **08–17**.

OOF claim jobs, calibration jobs and test-output jobs require independent review. The pipeline intentionally stops when these files are missing. These are research inputs, not unimplemented model routines.

The principal anchor family is DINOv2 fine-tuned joint-record prediction, seeds **0,1,2,3,4**. The other two backbones and frozen regimes are replication/ablation controls. Do not choose a successful seed for the headline.

## Recovery

Rerun an interrupted notebook with the same dataset/code/config. Feature extraction resumes completed shards. Training restores optimizer, model, scaler, epoch/batch position and RNG state. A changed config or source signature cannot reuse the same completed run silently.

For GPU out-of-memory errors, lower the microbatch before the main run and retain the effective batch through accumulation. An already-started run with changed training settings needs a separately recorded identity/amendment; do not relabel old weights. Local staging is recreated from the retained archive after a Colab reset.

Use different selected run IDs in concurrent sessions. Do not write one checkpoint directory from two runtimes. There are no keep-alive hacks or resource-limit bypasses.

## Publication and app

The full app is a later evaluated product. This release includes a local visual-prediction API and export path, not an App Store/Play Store application. FoodNExTDB research-only lineage is not automatically suitable for commercial deployment. Use the rights ledger and keep all parent assets in the lineage review.
