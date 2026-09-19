# Executable data contracts

All research files are versioned under the persistent root, outside the repository. This implementation uses **UTF-8 CSV, JSON/JSONL and NumPy NPZ**, rather than requiring Parquet. These are interchange choices, not target changes. `read_table` preserves strings/empty fields; numeric and boolean columns are explicitly converted by the consuming function. Boolean inputs must use true/false or 1/0.

## Public foundation

Official FoodNExTDB layout: participant CSVs named `A4F_XXXXX_labeled_data.csv`, fields `id,id_labeler,category,subcategory,cooking_style`, and images named by participant prefix. Only an unambiguous actual image association is accepted. Explicit JSON/list-valued parallel arrays are expanded together; unequal lengths stop. Ordinary comma-containing food names are not split. No cross-reviewer item ID, bounding box or preparation truth is inferred.

`records.csv`: record_id, image_path, participant_id/collection_group_id, domain, sha256, dhash, width, height, source, synthetic.
`annotations.csv`: record_id, reviewer_id, item_id, category, subcategory, cooking_style, source_file, row_number, reference_kind.

The negative target means **this eligible reviewer did not record this value**, not verified physical absence. A reviewer with a missing field in a relevant item bundle is excluded for that bundle. The fraction of remaining reviewers recording a label is the soft target. There is no conversion to a chemical or cancer-risk target. Class/tuple vocabularies are learned from fitting records only. Unseen held-out labels are saved, not mapped into convenient classes.

## New benchmark import

Place under `data/imports/<dataset_version>/`:

- `records.jsonl`: one record per independently defined meal/product capture episode, or explicitly defined focal task. Required: record_id, domain (`meal` or `product`), collection_group_id, image_path, rights_id, reference_status (`adjudicated`), cohort (`pilot`,`main`,`external`). Supply focal_item_id, household_pseudonym/session_id/batch_id/focal_product_family_id when applicable, and captured_at. Raw images must remain inside the approved import root.
- `annotations.jsonl`: record_id,item_id,reviewer_id,review_complete,adjudicated plus observed attribute fields. Preserve individual reviews; do not replace unknown fields with negative labels. For a declared focal task only that item's annotations enter its targets.
- `inference_states.json`: keyed by record_id, with focal_field,focal_item_id,visual_scope,sources. No support labels or hidden reference facts. `visual_scope` is `single_item`, `focal_crop` or `record_presence`. Whole-meal presence uses focal item `__record__`; otherwise supply a genuine inference-time focal crop/single-item input. Do not pretend a whole-meal tuple classifier localises an arbitrary item.
- `claim_rules.json`: finite field/value/qualifier menu, documentary requirements, review_status and actual review_reference. Model-predicted, recorded and observed statements remain different claim types.

Each visible source: source_id,record_id,item_id,source_type,facts,observed_at,available_at_inference,reference_only,verification_status,content_hash,conflict. Dates use timezone-aware ISO 8601. `verification_status: reviewed` requires a real review trail. Source text is data, not an executable instruction. A client saying “reviewed” is not sufficient for a production app.

## Focal item and pairing contract

Public models predict **record-level presence**, including complete food–method tuples. Item binding is not solved by choosing the highest image-level probability. New per-item tasks must supply a prespecified focal crop or single-item view at inference; the same task chooses the reference item before model outputs are inspected. A multi-item full-frame task can remain record-presence; this does not support arbitrary item-specific assertions. `crop_focal_image` consumes an explicitly supplied box, not an oracle-derived test mask.

## Reference/rating files

Generated blind jobs include candidate_id,record_id,field,value,qualifier,input_mode,blinded_job_id. Reviewers add reviewer_id,factual_status,evidential_status,informative,reason_code and adjudication_id. Adjudicated files contain one resolved record per candidate_id, with the originals retained separately.

Factual status: supported,contradicted,unknown/unverifiable.
Evidential status: supported,unknown/unverifiable/unsupported.
Combined supported requires both axes satisfied. Contradicted and unverifiable are retained separately. Noninformative wording cannot raise useful coverage. Missing ratings stop evaluation rather than becoming supported by default.

Paths under `private/<dataset>/claims/<run_id>/<input_mode>/`:
`validation_ratings_adjudicated.csv`, `calibration_ratings_adjudicated.csv`, `test_ratings_adjudicated.csv` correspond to generated jobs. OOF ratings live next to `runs/<dataset>/oof/<run_id>/oof_claim_rating_jobs.csv`.

## Clarification

`fitting_action_episodes.csv` includes split=fit, action_id and inference-only selector features, independently assessed supported_gain/unsupported_gain, cost_units. All four actions require actual coverage; do not fabricate missing counterfactual rewards. Features must be generated out of sample for the policy’s development analysis.

`documented_answers.jsonl`: record_id,action_id,available,source_id,elapsed_seconds and an actual `source` object when available. Missing answers stay unknown. The replay condition is idealised documented information, not human response accuracy. After-output ratings remain independent.

## Pilot/user/lab contracts

Pilot reviews: record_id,reviewer_id,attribute,value,minutes. Precision input: one independent group_id/risk_difference row, from actual pilot comparison.
User outcomes: participant_id,arm,comprehension_correct,appropriate_reliance,elapsed_seconds. The provided analysis is a parallel-arm participant-bootstrap analysis, not a crossover or a cancer-outcome model.
Assay rows: specimen_id,analyte,batch_id,concentration,lod,loq,censored,units,qc_pass. Units must be harmonised. Technical replicates are not new specimens. No LOD/2 imputation is silently performed; the detected-only Ridge comparison is explicitly an exploratory sensitivity analysis, not the primary censored model.

## External cohort after lock

Do not rerun the main split notebook on an enlarged dataset. Notebook 22 creates a separate cohort directory and lock, applies the fixed train-only vocabulary, and checks known links to main data. Fresh-prospective capture must follow the parent lock; earlier external data need a separately registered retrospective protocol. Source/input/reference files and group review remain auditable.
