# Release validation — OncoPlate v3.0.0

Validation performed on 18 September 2026 in a CPU-only Linux environment, not a Colab GPU runtime. The test logs and machine-readable summary are in `reports/software_validation/`.

## Executed successfully

| Check | Observed result |
|---|---|
| Unit/integration suite | **92 passed**, no failed tests |
| Notebook JSON/schema validation | **29 notebooks passed** |
| Notebook code-cell compilation | **139 code cells passed** |
| Notebook imports against repository functions | Passed as part of the test suite |
| Notebook 00, environment/permissions | Executed end to end locally |
| Notebook 90, isolated software demonstration | Executed end to end locally |
| Interrupted optimizer-boundary checkpoint recovery | Resumed CPU predictions exactly matched the uninterrupted fixture run |
| End-to-end synthetic pipeline | Targets, group splits, two frozen heads, four-fold OOF selectors, calibration, policy lock, sealed test access, group bootstrap, TorchScript export |
| Fine-tuning execution | CPU fixture encoder parameters changed under training |
| Backbone interfaces | ResNet-50 and ConvNeXt-Tiny forward passes with random weights; not pretrained food-recognition evaluation |
| Research API and mobile-sized web interface | Local test client; image response contract, no cancer-risk output, no retained upload |
| Safe installer | Correct checksum required; traversal rejected; existing checkout preserved |

The demo uses artificial colour arrays, not photographs of food. It records **zero biological/scientific food experiments**. No demo metrics belong in a research-results table. Software-fixture labels and adjudications are generated only in the isolated DEMO_ONLY path.

## Not executed or established here

- FoodNExTDB's complete archive download and actual archive-schema integration. The adapter follows the inspected official schema and fails explicitly when files do not match it.
- Downloads or forward passes of pretrained DINOv2, Qwen2.5-VL or SmolVLM weights; exact remote snapshots are pinned when the user runs them.
- Full GPU fine-tuning, mixed-precision GPU execution, the 60-run panel, real-data results, real-data annotation agreement, or prospective evaluation.
- ONNX conversion or on-device phone inference. TorchScript parity was tested on local fixtures; TorchScript emits deprecation warnings in the tested torch version. ONNX is an optional path to retest in the target environment.
- Approval, ethics, independent documentary references, claim adjudications, rights clearance, laboratory measurements, or human participant outcomes.
- Exact reproduction of FoodCHA/ConfLVLM or any other named published method. Included direct/staged VLM and grouped binary-set comparators are labelled adaptations; protocol-fidelity review remains necessary.
- Native Android/iOS packaging, app-store release, clinical utility, cancer-risk prediction, or assay-based food chemistry.

## Environment actually tested

Python 3.13.5; torch 2.10.0+cpu; torchvision 0.25.0+cpu; NumPy 2.3.5; pandas 2.2.3; scipy 1.17.0; scikit-learn 1.8.0; pytest 9.0.2; nbformat 5.10.4; nbclient 0.10.4. Re-record the environment in notebook 00 on each new Colab runtime. Package constraints are not a claim that every allowed dependency combination was tested.

## Why later notebooks may stop

A missing approval reference, actual dataset, blinded rating file, finite reviewed claim schema, source record or locked model is a genuine dependency. The code does not fabricate it. Notebook 90 is the only deliberately synthetic end-to-end path. Read `DATA_CONTRACTS.md` and `BASELINES_AND_LIMITATIONS.md` before collecting or importing research data.

`registries/run_id_mapping.csv` maps the accepted plan's verbose run IDs to the implemented short IDs; the model/backbone/head/seed design is unchanged.
