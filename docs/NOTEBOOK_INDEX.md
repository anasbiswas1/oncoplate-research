# Notebook execution map

Start with 00 and 90, then 01–05. The main 06–17 track needs real pilot/benchmark data and approvals. Supplements do not replace those requirements.

| Notebook | Purpose | Prerequisites |
|---|---|---|
| `00_environment_and_permissions.ipynb` | 00 · Environment, persistent paths and recorded permissions | Start here after installation. No GPU or new data are required to initialise the workspace. |
| `01_public_dataset_audit.ipynb` | 01 · FoodNExTDB download, schema and image audit | Requires actual supervisor execution and research-use terms decisions. The adapter checks the published schema and stops rather than guessing malformed records. |
| `02_claims_and_reference_schema.ipynb` | 02 · Attribute, reference and source contracts | Run after the data audit. The proposed schema is not automatically domain-approved. |
| `03_group_graph_and_splits.ipynb` | 03 · Leakage graph, frozen partitions and training targets | Requires audited records and completed duplicate review. Split membership does not change with model seed. |
| `04_feature_smoke_test.ipynb` | 04 · ResNet feature-extraction smoke test | Run only after notebook 03. Start on a fitting-only subset; this is debugging, not a paper result. |
| `05_seed0_baselines.ipynb` | 05 · Frequency, attribute and complete-record baselines | Run after the smoke test. This notebook does not open test labels. |
| `06_pilot_quality_and_precision.ipynb` | 06 · Real pilot quality, effort and precision planning | Requires the approved real pilot; synthetic outputs never supply sample-size evidence. |
| `07_new_benchmark_ingestion.ipynb` | 07 · Ingest the documented OncoPlate benchmark | The flagship starts here after the pilot. Actual source records, references, data rights and reviews are needed. |
| `08_frozen_and_finetuned_grid.ipynb` | 08 · Full 60-run backbone × regime × head × seed grid | Run after seed-0 validation and the pilot-informed configuration freeze. This preserves the full resource-intensive design. |
| `09_oof_selector_training.ipynb` | 09 · Grouped out-of-fold predictions and matched support selectors | Use the flagship benchmark for claim support. Foundation annotation agreement is a different target, analysed separately in notebook 21. |
| `10_source_gate_and_ablations.ipynb` | 10 · PCSI source gate, candidate audit and ablations | Run after OOF training; candidate inference never uses the reference table. |
| `11_clarification_replay.ipynb` | 11 · Equal-budget clarification from documented episodes | Requires actual fitting action episodes and available answers. Missing answers remain unknown; replay is not a real-user study. |
| `12_calibration_and_lock.ipynb` | 12 · Calibration, validation thresholds and immutable analysis lock | Flagship only. All five anchor seeds need OOF selectors and independently adjudicated calibration/validation claims. Do not use this notebook to bypass missing data. |
| `13_sealed_and_external_test.ipynb` | 13 · Sealed internal test and blinded output assessment | Run only after notebook 12. Initial inference generates independent rating jobs; a later cell joins actual adjudications without changing predictions. |
| `14_grouped_statistics.ipynb` | 14 · Grouped, paired, seed-separated statistical analysis | Requires fixed predictions and independently adjudicated outcomes from notebook 13. |
| `15_mobile_export_and_retest.ipynb` | 15 · Export, compression and deployment parity | Exports a visual predictor for research, not a complete medically validated app. Rights and the source/selection engine remain separate. |
| `16_user_study_analysis.ipynb` | 16 · Approved comprehension and appropriate-reliance study | Run only with independently collected participant outcomes and a documented user-study decision. This is not a cancer-incidence study. |
| `17_paper_reproduction.ipynb` | 17 · Reproduce paper tables, figures and evidence index | This notebook regenerates outputs from saved results. It does not invent missing experiments or write a results section from the plan. |
| `18_vision_language_baselines.ipynb` | 18 · Local vision-language and staged-attribute comparators | Optional heavyweight model comparisons. These are documented adaptations, not claimed exact FoodCHA or ConfLVLM reproductions. |
| `19_product_and_ingredient_tracks.ipynb` | 19 · Product lookup and external ingredient metadata | Product/ingredient information is not a chemical assay. Access and source licences require review. |
| `20_robustness_and_binding.ipynb` | 20 · Source, wording, corruption and food–method binding tests | Run controlled development diagnostics before test lock; later stress tests must be prespecified and reported separately. |
| `21_foundation_calibration_and_selection.ipynb` | 21 · FoodNExTDB calibration and annotation-agreement selection | This gives an immediately executable public-data research baseline after notebooks 00–05. It is not the flagship cancer-relevant claim-support experiment. |
| `22_fresh_external_cohort.ipynb` | 22 · Fresh external-cohort addendum without retuning | Run after the main analysis lock and fresh collection. It does not rebuild or overwrite the main split or vocabularies. |
| `23_optional_group_prediction_sets.ipynb` | 23 · Optional grouped binary-support prediction sets | Secondary adapted analysis, not a reproduction of a named paper or a selective-error guarantee. Reserve its calibration protocol before final testing. |
| `24_hyperparameter_development.ipynb` | 24 · Pre-test hyperparameter search with separate run identities | Optional development search. Never reuse a completed run directory for a changed learning rate. |
| `25_mobile_research_api.ipynb` | 25 · Local research API contract and smoke test | Development API only. No public tunnel, authentication bypass, remote participant upload or medical release is created. |
| `26_foundation_convergence.ipynb` | 26 · Foundation convergence against the frequency baseline | Development check on validation and the calibration partition. Test records are not read. |
| `27_foundation_prior_init.ipynb` | 27 · Base-rate initialised heads against the frequency baseline | Amendment check on validation and the calibration partition. Test records are not read. |
| `28_foundation_prior_init_calibration.ipynb` | 28 · Calibration and selective prediction on base-rate initialised heads | Validation comparison of calibrators and abstention with participant-group intervals. Test records are not read. |
| `90_offline_end_to_end_demo.ipynb` | 90 · Isolated end-to-end software demonstration | Runs on CPU without data/model downloads. Artificial colour arrays are software fixtures, not meals or research observations. |
| `99_manual_git_review.ipynb` | 99 · Manual source-control and release review | Read-only by default. Never commit raw images, per-person labels, private predictions, source records, tokens or checkpoints automatically. |
| `L01_assay_pilot.ipynb` | L01 · Optional assay pilot provenance and analysis | Requires an analytical collaborator, actual laboratory data and separate authorisation. Nothing in this notebook specifies wet-lab procedures or invents concentrations. |
