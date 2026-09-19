# Troubleshooting

**Missing repository:** run the standalone installer or set ONCOPLATE_REPO. An installation pointer supports an existing checkout without overwriting it.

**PermissionError:** inspect the exact named gate. Enter only genuine decision references. Demo checks do not require a real-study gate.

**Data archive schema mismatch:** inspect the actual CSV, filenames and list structures in notebook 01. The archive was not available here. Do not rename arbitrary files, construct item pairings from a Cartesian product, or force the expected published count. Preserve a small de-identified schema sample for code review.

**Colab runtime reset:** remount Drive, repeat environment checks, restore local staging, rerun the same notebook. Feature shards and optimizer checkpoints persist outside the runtime. Do not put extracted 9,000-file training loops directly on Drive unnecessarily.

**CUDA out of memory:** confirm the GPU and actual VRAM. Choose a smaller microbatch, retain the intended effective batch via accumulation, and record settings. Feature extraction can resume existing shards with a smaller batch. A training-setting change must use a new run identity/version rather than reusing an incompatible partial checkpoint.

**Run signature mismatch:** data, target schema, code or settings differ from the saved run. This is deliberate protection. Restore the original environment/config or make an explicit amendment/new output directory; do not delete run.json and pretend the experiment is unchanged.

**DINO or VLM import error:** install the optional Transformers 4.57.1/Accelerate/HF stack in notebook 18, then restart the runtime if imported modules are stale. Do not blindly upgrade/downgrade torch/torchvision independently. Save the actual working pip freeze.

**Review file missing:** generated jobs need independent reviewers. No notebook invents support labels, clarifications or assay measurements to let Run All continue.

**No informative answers:** report achieved coverage and undefined conditional risk. Do not map unknown foods into an easier class or replace thresholds from test labels.

**External import rejected:** check new capture timestamps and group/product/duplicate overlap. Keep main targets immutable after lock. A retrospective external dataset needs its own documented protocol, not a fake future timestamp.

**Git warning:** raw/private files are not automatically publishable. Use an authenticated Git client and a reviewed branch. Never place tokens in notebook source, outputs, remotes or ZIPs.
