# OncoPlate v3.0
## Master Research-to-App Work Plan

**Evidence-grounded multimodal recognition and selective guidance for cancer-relevant dietary choices**

Prepared for **Md Anas Biswas** | 18 September 2026  
Programme direction: accepted by the project owner in this conversation.  
Execution status: upgraded planning baseline; not an institutional approval, frozen preregistration, completed experiment, or release authorisation.

### The decision

Replace the retired cancer-exposure-tier classifier with a substantial research programme that combines photographs, documented ingredients and preparation, source-aware uncertainty, targeted clarification, and reviewed dietary evidence. Produce one integrated methods-and-benchmark paper, then a validated mobile prototype. Investigate laboratory chemistry as a parallel, separately governed extension; it does not block the core paper.

**Immediate deliverable:** a reviewed claim schema, audited public-data baseline specification, and approved pilot-collection protocol. **First experimental milestone:** an auditable dataset, leakage-safe splits, reproducible seed-0 models, and saved validation predictions. **Flagship deliverable:** a new documented-record benchmark plus an evaluated method that improves supported information without hiding behind blanket abstention.

### How to use this plan

Sections 1–5 fix the scientific target. Sections 6–12 specify data, methods, comparisons and analysis. Sections 13–16 define work packages, notebook implementation order, resources and gates. Sections 17–20 connect the paper to a responsibly scoped app and optional laboratory study. The companion planning pack contains machine-readable task, experiment, evidence and annotation templates. These are planning assets, not implemented training notebooks.

**Evidence convention.** [S1] refers to the supplied v1.2 plan; [S2] to the supplied v1.3 runbook and the accepted direction in this conversation. Numbered references [1]–[21] are externally checked sources. Unreferenced design choices, counts, schedules, thresholds and method definitions below are new proposals. They are not reported findings or externally established standards. The parent programme proposal named inside v1.2 was not supplied and has not been reconstructed.

---

# 1. Scope, commitments and migration from June

The June plan established the project, repository convention, participant grouping, five seeds and supervisor-review gate. The September v1.2 amendment correctly retired PROTECTIVE/LOWER/MODERATE/HIGH as the primary endpoint but retained contradictory operational sections. This document replaces those active instructions rather than layering another warning on top of them. [S1, Sections 0, 7, 9 and 13]

| Earlier design | v3.0 replacement | Consequence |
|---|---|---|
| Four ordinal exposure tiers | Separate food, processing, preparation, surface-appearance and evidence-availability attributes | No arithmetic on IARC groups; no meal cancer-danger score |
| Public data only | Public-data foundation plus a newly documented multimodal benchmark | New collection and annotations require approved protocols and resources |
| Option D as the novelty | Standard calibration controls plus a source-aware selection method | Arbitrary 30-example calibration switch is not a contribution |
| Food recognition as the complete paper | Recognition as a component of reliable dietary-information delivery | Novelty tested against structured and selective baselines |
| Reference-informed abstention | Inference from permitted inputs only | Reference-informed routing remains an explicitly labelled oracle |
| App after publication with unspecified data rights | Parallel product-permission and model-lineage planning | Research-only assets are not silently transferred to a product |
| Appearance treated as chemical exposure | Appearance classification kept separate from any measured chemical target | Chemistry claims require paired assays |

**Version policy.** Archive v1.1, v1.2 and the old proxy-label code without deleting them. The v1.3 runbook remains a foundation-work-package reference, not the whole programme. Mark this file v3.0; reserve v3.1 for pilot-informed changes and v3.1-LOCKED for the eventual preregistered analysis. Record every change with a reason, date, author and whether any test outcome was visible.

**Approval policy.** The user's acceptance resolves the direction and willingness to undertake heavier work. It does not establish supervisor approval, ethics approval, a domain reviewer, funding or permission to commercialise research assets. The original supervisor gate before new executable scaffold/notebooks remains pending until documented. Planning, review preparation and resource enquiries can proceed now. [S1, lines 13, 239–245]

# 2. Intended use and explicit exclusions

**Initial intended function:** help adults identify cancer-relevant food characteristics, understand the evidence and its limitations, and obtain more reliable information by supplying product or preparation details. The initial research prototype is educational decision support for general dietary choices, not a diagnostic or personalised cancer-risk tool. Its legal classification must nevertheless be assessed rather than presumed. [17]

The first benchmark centres on processed-meat identification, mammalian red-meat identification, correctly bound preparation attributes, missing-information recognition, and evidence-card fidelity. Vegetables, pulses, fish, poultry, plant-based products and mixed dishes are included as comparison and ambiguity cases, not assigned blanket protective or safe labels.

WHO/IARC distinguishes the strength of carcinogenicity evidence from the size of a person's risk: processed meat is Group 1 and red meat Group 2A, with different evidence descriptions. These classifications must remain source-attributed metadata; they are not image classes ordered by meal danger. [1]

**Excluded from version 1:** cancer diagnosis; individual cancer probabilities; all-carcinogen detection; a universal safe/unsafe food list; inferred chemical concentrations without assays; allergen certification; freshness or pathogen guarantees; clinical dietary management for active cancer treatment; automatic calorie or portion precision from one image. Do not use NOVA category, an additive code, colour darkness or a missing label as a substitute for any of those claims.

No advice should encourage undercooking food to avoid charring. No output should imply that failing to establish a cancer-related attribute establishes safety. Product formulations, user answers and database records can be wrong or incomplete; their provenance and uncertainty remain visible.

**App language example, not a generated finding:** “The image resembles a sausage-style product. Processing status is not established. Scan the package or provide preparation information for a more specific assessment.” A reviewed evidence card can then explain the general evidence, without converting resemblance into confirmed processing.

# 3. Research contribution and questions

**Proposed paper title:** *OncoPlate: Evidence-Grounded Multimodal Recognition and Selective Guidance for Cancer-Relevant Dietary Choices*.

**Core hypothesis:** a policy that reasons about the provenance and sufficiency of required premises will provide more supported, specific information than confidence-only selection, at comparable coverage and information-acquisition cost. This is a testable hypothesis, not an established innovation claim.

| Question | Experiment | Evidence needed |
|---|---|---|
| RQ1: Where do unsupported assertions arise? | Compare image-only, metadata-only and multimodal systems | Separate recognition mistakes, wrong food–method binding, missing premises and inaccurate evidence statements |
| RQ2: Does source-aware selection help? | Same candidate predictions, inputs and output budget; compare generic selection with the proposed gate | Lower unsupported-assertion rate without unacceptable loss of useful coverage |
| RQ3: Which additional information helps? | Fixed, random, uncertainty-based and proposed questions at the same budget | More supported information per action, with unanswered and erroneous replies included |
| RQ4: Does the result generalise? | Group-disjoint, domain-held-out and fresh prospective tests | Consistent estimates and honest failure analysis across collection settings |
| RQ5: Can it be deployed without losing reliability? | Compression, device and missing-network tests | Latency/memory measurements plus recalibration and claim-error analysis |
| RQ6: Do users understand the output? | Controlled interface evaluation after technical validation | Appropriate reliance, comprehension and burden; not cancer-incidence reduction |

**Three candidate contributions:** a documented multimodal reference benchmark; a source-aware claim-selection and clarification policy; and an integrated external/prospective evaluation connected to a mobile prototype. A new name, three backbones, a calibrated classifier or the combination of existing components alone will not establish methodological novelty.

# 4. Prior art and what to compare

This is a focused source refresh to inform execution, checked on 18 September 2026. It is not a systematic review and does not establish priority or absence of all competing work. Create a living search log and rerun it before method freeze and submission.

| Prior art | Established contribution relevant here | Required treatment |
|---|---|---|
| FoodNExTDB and its source paper [4,5] | Expert visual food annotations and dietary-recognition evaluation | Public-data foundation; not preparation or chemical truth |
| FoodCHA, preprint [8] | Staged category, subcategory and cooking-style prediction | Implement a documented comparable structured baseline; do not call hierarchy new |
| OmniFood-Bench, preprint [9] | Food perception, nutrient reasoning and health-advice evaluation | Explain why new documented records and source sufficiency add information |
| ConfLVLM, EMNLP 2025 [10] | Conformal-style filtering of generated visual claims | Claim filtering is prior art; any adaptation must state its changed task and assumptions |
| Budgeted conformal evidence acquisition, preprint [11] | Re-examination through crops, zooms and interventions | Separate same-image reinspection from genuinely new ingredient/preparation information |
| Hierarchical selective classification [12] | Less-specific outputs under uncertainty | Include a specificity-aware comparator rather than binary rejection only |
| Crowd-Calibrator, COLM 2024 [13] | Disagreement-aware calibration and abstention | Annotator disagreement alone is not the new algorithm |
| Attribute-binding / ARO work [14] | Compositional failures and attribute swaps | Food–method swap diagnostics adapt an established idea |
| Temperature scaling [15] | Standard post-hoc probability calibration | Calibration baseline, not a headline novelty |
| Hierarchical conformal inference [16] | Inference with grouped or repeated measurements | Specify the actual sampling unit and guarantee rather than invoking conformal generically |

Record study/report identity to avoid counting a conference paper and its extended report as two studies. For each paper save identifier, version, exact title, source checked, verification level, access date, task, information available, reference standard, comparator role and limitations. Do not infer implementation details from an abstract.

**Verification exception:** v1.2 mentions IntroConformal (arXiv:2609.01375). Its primary arXiv endpoint could not be re-fetched in this pass. Keep it in the verification queue, not the verified baseline list; this is not a claim that the study is invalid or nonexistent. The earlier broad “first-ever” assertions are not carried forward.

# 5. Claim schema and reference standard

A claim is an atomic statement with a defined subject, attribute, value, epistemic qualifier, evidence requirements and permitted wording. The same finite menu is available to all systems in the primary experiment. Open-ended prose is secondary.

| Claim family | Required information | Permitted output / restriction |
|---|---|---|
| Food identity | Auditable visual prediction or documentary source | Explicitly predicted when based on a model; reference uncertainty retained |
| Animal-source class | Relevant ingredient or recipe record, or qualified prediction | Mammalian meat and processing are separate attributes |
| Processing status | Reviewed ingredient/preparation evidence meeting the operational definition | “Recorded as processed meat” is distinct from “looks like a sausage” |
| Preparation method | Method attached to the correct food item | Never transfer a side dish's method to the meat |
| Surface appearance | Image and independent appearance annotation | “Visible dark surface” is not a chemical measurement |
| Information missing/conflicting | Missing required fields or unresolved source disagreement | Identify the missing premise and the useful next input |
| General cancer-evidence card | Reviewed, versioned source entry | Attribute the evidence, preserve scope, do not personalise risk |
| Logged pattern summary, later stage | Confirmed foods, quantities and log completeness | Quantified comparisons only when supporting records permit them |

**Two reference axes must be scored separately.** Factual status asks whether the complete reviewed record supports, contradicts or cannot establish the claimed attribute. Evidential status asks whether the inputs actually available to the system support the strength of its wording. A statement can happen to be factually correct but be presented with unjustified certainty. Conversely, a qualified prediction should not be penalised as an unqualified assertion.

For the primary endpoint, a claim is **supported** only when its factual status and evidential requirements are both satisfied for the registered claim type. **Contradicted** means a reference conflict exists. **Unverifiable** means the record or available premise does not establish it. **Non-informative** means generic wording that fails the task's prespecified specificity criterion. Preserve the component labels; do not conceal the distinction inside one score.

Develop the rubric independently of the proposed algorithm. Apply it identically to baseline outputs. Two trained reviewers independently construct the main reference record; a domain-qualified adjudicator handles disagreement. For the pilot, use three independent reviews to test whether the schema is understandable. Keep original reviews as well as adjudication. Domain interpretation must not be delegated solely to the model being tested.

**Prevent the empty-answer shortcut.** Missing-information messages remain useful in the interface but do not count as answered focal claims. Generic educational cards, restating “food is present”, and repeating the same fact do not increase informative coverage. Evaluate appropriate missing-information detection as its own endpoint.

# 6. Dataset programme and feasible scale

The new collection is primary for the flagship experiment. Public data provide warm-start experiments and secondary validation of overlapping attributes, not a substitute for the new reference standard.

| Resource | Proposed role | Boundary |
|---|---|---|
| FoodNExTDB [4,5] | Reproduce attribute/tuple foundation and disagreement analysis | Research-only; public annotations are not chemical ground truth |
| Nutrition5k [6] | External ingredient-presence and recorded-mass checks | Only overlapping tasks; do not invent cooking-style or chemical labels |
| Open Food Facts [7] | Product-information branch and lookup testing | Verify current package, preserve retrieval provenance and licence obligations |
| New OncoPlate records | Main claim-support and clarification benchmark | Rights, ethics and quality must be established |
| Optional laboratory specimens | Paired measurement extension | Analysed separately from visual annotations |

**Planning target, not a power calculation:** 100 pilot records, 2,400 main records and 400 fresh prospective/external records. Pilot records remain outside confirmatory evaluation. Within main and external sets, budget approximately 60% meals and 40% packaged products: main 1,440/960 and external 240/160. The total is 2,900 distinct records including the pilot, not 2,900 independent observations. Multiple views do not multiply the sample size.

A meal record represents a specific preparation and serving episode; a packaged-product record represents a specific product/formulation and capture episode. Photograph a meal from two or three useful viewpoints and collect relevant package or preparation evidence separately. Keep original capture time, preparation/batch IDs and the relation between focal items. Do not duplicate photographs and relabel them as fresh meals.

Target diversity across realistic single- and multi-item meals, preparation conditions, product formulations, phone cameras, lighting and backgrounds. Start with a UK collection context; include South Asian and other cuisine strata through actual recruitment and records, not inferred ethnicity. A Bangladesh collection is optional and requires local arrangements and transfer review before it is labelled an external site. Cuisine diversity in one kitchen does not establish geographic generalisation.

Aim initially for at least 120 independent main acquisition groups and 60 fresh external groups; these are recruitment design targets, not statistical sufficiency thresholds. Revise the required group counts using the pilot. A dataset with many images but very few kitchens or product families may fail the intended precision requirement.

**Challenge cases:** visually similar processed/unprocessed products; meat/plant-based lookalikes; sauces versus surface darkening; mixed meals with swapped food–method associations; incomplete ingredient records; stale product entries; unsupported “no additives” inferences; contradictory user answers. These stress sets are reported separately from the ordinary collection and do not estimate their real-world prevalence.

# 7. Collection and annotation procedure

**Step A — authorisation.** Obtain the supervisor and institutional determinations relevant to collection, participant recruitment, privacy, data sharing and product reuse. Prepare participant information, consent and withdrawal procedures where required. Do not assume food photographs are anonymous when they contain people, receipts, location data or links to personal logs.

**Step B — record creation.** Assign record, household/collector, kitchen/session, recipe/formulation, focal product-family and batch IDs. Store contact details outside the research manifest. Capture raw photographs and documentary evidence, remove unneeded identifying information from working copies, and preserve checksums and private provenance.

**Step C — image-only pass.** Reviewers see only the declared image input. They annotate visible attributes, candidate alternatives, item–method associations and what they cannot establish. They do not see model outputs or hidden reference records.

**Step D — documented-record pass.** Different blinded passes inspect the permitted ingredient panel, preparation log or manufacturer information. They assign each fact a source, timestamp, scope and confidence category defined in the rubric. A package statement is evidence of its declared composition, not an assay of chemical concentration. A user recollection is not automatically as reliable as a contemporaneous log.

**Step E — disagreement handling.** Preserve both records, adjudicate conflicts, and mark facts unresolved when evidence is insufficient. Do not silently transform disputed observations into negative labels. Record source conflict as a feature available to all methods when those sources are supplied.

**Step F — test-reference sealing.** Lock reviewed reference records and predefined claim assessments before inspecting test outputs. Later natural-language outputs are de-identified, randomly ordered and rated by blinded reviewers. Deduplicate identical record/input/claim combinations to reduce workload without creating artificial independent observations.

**Pilot exit:** the schema represents the collected data; identities are traceable; the reviewers can apply the rubric; unknowns remain explicit; leakage grouping is feasible; rights and storage are documented; time per annotation and disagreement rates have been measured. Failure triggers a schema or collection amendment before expansion, not a convenient relabelling rule.

# 8. Splits, leakage and sample-size planning

Keep source datasets separate. Do not combine FoodNExTDB, product lookups and the new collection into one randomly split table.

For the 2,400-record main benchmark, use approximately **48% fitting / 12% development validation / 20% probability calibration / 20% sealed test**, allocated by independent groups. The arithmetic targets are 1,152/288/480/480 records, but actual record counts follow grouping, not the other way around. Split seed 0 is fixed. Model seeds 0–4 vary training, not the test membership.

Build a leakage graph linking repeated views, exact/near duplicates, the same household, preparation session/batch, and near-identical focal product formulations. Keep connected components together. A generic ingredient type, retailer or country is a domain label, not automatically an edge joining the entire collection. Specifically audit product-family overlap between meal and product branches. When this creates an oversized component, redesign acquisition rather than breaking it to improve counts.

Reserve the 400 external/prospective records for after algorithm and interface-input contracts are frozen. They must involve new collection groups; ideally an independent collection team or setting. Record whether the test is genuinely external, merely later-in-time, or both. Do not claim external validation from a new phone photographing the same meals.

**Pilot-based precision analysis.** Estimate event frequencies, between-group variation, intragroup dependence, abstention and the likely paired method difference. Simulate the complete sampling and evaluation procedure across candidate numbers of groups and records per group. Set a meaningful effect size and confidence-interval precision with domain and statistical review before collecting the final evaluation cohort. Include scenarios with more unknown labels and higher abstention than expected.

The planning aim is to detect an absolute difference of around five percentage points in unsupported assertions near 80% useful-answer coverage; this is not a performance promise or clinically validated safety threshold. Adjust the design if the pilot cannot support that comparison. Document the revision before test unblinding.

If an independent test reviewer discovers a broken reference record, apply the same prespecified correction/exclusion policy to all systems and preserve an audit trail. Do not remove hard cases based on model errors.

# 9. System and proposed method

**Working method label:** provenance-constrained selective inference (PCSI). This is descriptive terminology, not a verified first-ever algorithm name.

The architecture has five components: an image/record attribute predictor; a source-and-conflict ledger; a finite reviewed claim engine; a learned selection/acquisition policy; and a controlled response renderer. Item-level bindings are preserved end to end. The renderer cannot invent a stronger statement than the selected claim permits.

### 9.1 Source ledger and candidate states

Represent the current state as s = (image evidence, available metadata, provenance, unresolved fields, source conflicts). Attribute predictions are distributions, not confirmed facts. Candidate complete states Z(s) retain compatible ingredient and method alternatives, including an explicit unknown alternative. Do not prune a missing processing status solely because its most likely value is high-confidence.

Each claim c has a reviewed predicate P(c,z), required source conditions A(c,s), a specificity level and evidence-card ID. Its deterministic eligibility is:

**G(c,s) = A(c,s) AND no unresolved critical conflict AND P(c,z) holds for every retained z in Z(s).**

For a qualified visual prediction, P and A are defined for that weaker statement; documentary confirmation is not falsely required for every image-recognition claim. For an unqualified processing assertion, the source requirements are stronger. Any conflicting or empty completion set produces an error/abstention state, never vacuous support.

This gate is conditional on a finite schema and the alternatives it retains. Approximate top-k search can exclude the truth. Track discarded probability mass, retain an unknown alternative and run candidate-size sensitivity tests. Do not call the resulting procedure a clinical or distribution-free guarantee.

### 9.2 Learned selective score

Train a support predictor using candidate confidence, joint-versus-marginal disagreement, missing-premise indicators, source type, source age, conflict indicators and evidence-template ID. Produce an empirical estimate of whether the claim will meet the independent support rubric. Use out-of-fold predictions within the fitting partition to train this selector; in-sample confidence would contaminate its training problem.

Compare a regularised logistic selector and a small neural selector with the same inputs. The principal ablation removes the provenance and missing-premise components while keeping classifier capacity, candidate generator and calibration identical. A rules-only implementation separates the value of the deterministic gate from the learned component.

A claim is emitted only if eligible and its calibrated support score meets the frozen threshold. When a stricter claim fails, consider an allowed lower-specificity claim; otherwise return the missing-information message without counting it as informative task coverage.

### 9.3 Clarification policy

Allowed actions are finite: request a package/barcode lookup, request an ingredient-panel image, request a food-component clarification, or ask for a preparation detail. The ordinary primary action budget is zero; the key acquisition experiment allows at most one new action. Two-action results are secondary.

Learn expected gain from recorded development episodes: **expected additional supported information minus unsupported-output penalty minus question cost**. Use the same action menu and budget for fixed-question, random, uncertainty-only and proposed policies. Choose the penalty and cost weights before test access. Report actions and elapsed user time separately rather than relying only on an arbitrary combined utility.

Offline replay returns an answer only when the documented record actually contains it. Otherwise return “unknown”. Call the complete-record replay an idealised documented-answer condition; it does not establish how users answer in practice. The prospective evaluation uses real responses and records refusal, mistakes and contradictions.

### 9.4 Testable properties, not universal guarantees

Test information-loss monotonicity for the deterministic completion operator: with fixed predicates and candidates, deleting information should not increase its set of unqualified eligible claims. Do not claim the complete learned pipeline has this property automatically when its predictions are recomputed.

Test item-binding consistency, source-conflict handling, missing-evidence routing, and faithful rendering against executable specifications. Constructed food–method swaps are diagnostic report perturbations, not physical counterfactual meals or causal chemical experiments. [14]

# 10. Experimental matrix

### Model panel

Use ResNet-50, ConvNeXt-Tiny and DINOv2 ViT-S/14 as reproducible cross-family controls. This intentionally substitutes the documented TorchVision ConvNeXt-Tiny implementation for the earlier ConvNeXt-V2-Tiny proposal; record the change rather than confusing the two models. Use explicit checkpoint identifiers and preprocessing contracts. These are controlled baselines, not a claim to represent the latest best architecture. [19–21]

For each backbone compare frozen features and fine-tuning, and compare independent attribute heads with a complete-record head. Across five seeds this gives **3 × 2 × 2 × 5 = 60 principal predictor fits**. Feature extraction can be shared where legitimate. Hyperparameter search, out-of-fold fits, selectors, calibration and multimodal adaptation add runs; do not call 60 the total compute budget.

Select two accessible vision-language model families at the development gate, recording exact snapshots, licences and any data-retention conditions. Include a FoodCHA-style staged comparator using accessible code or a fully documented reimplementation. A reimplementation is not called a reproduction unless protocol fidelity has been established. Unsupported or inaccessible models remain an acknowledged comparison limitation, not fabricated results. [8]

### Method comparisons

| ID | Method | Role |
|---|---|---|
| M0 | Training-frequency / metadata-only deterministic baselines | Expose label-prior and documentary shortcuts |
| M1 | Independent attribute predictor with calibrated rejection | Standard marginal-confidence baseline |
| M2 | Joint-record predictor with calibrated rejection | Strong binding-aware baseline |
| M3 | Same candidates plus generic learned selector | Main controlled comparison for PCSI |
| M4 | Hierarchical selective output | Tests whether ordinary coarsening is sufficient |
| M5 | Adapted factuality/conformal filter | Secondary comparison; changed assumptions disclosed |
| M6 | Source rules only, without learned selector | Isolates the benefit of rules |
| M7 | Full PCSI, no additional question | Primary method contrast against M3 |
| M8 | PCSI plus budgeted clarification | Key secondary acquisition comparison |
| M9 | Reference-informed oracle | Diagnostic upper bound, never deployable headline |

Evaluate image-only, metadata-only and image-plus-available-metadata tracks separately. In the main M7 versus M3 contrast, use the same frozen multimodal candidate generator, same available inputs, same candidate set and same one-focal-claim output budget. The test task/claim family is specified independently of hidden ground truth. Candidate selection cannot consult the reference record. The DINOv2-based fine-tuned predictor is the prespecified anchor; the other backbones test replication, not best-result selection.

Acquisition comparisons give every method the same initial state, menu, resource budget and response process. Report performance before and after additional information. Never credit the algorithm alone for an improvement caused by giving it information withheld from its comparator.

### Hyperparameters and calibration

Run seed 0 smoke tests before the full grid. Use masked multi-label losses where multiple items/attributes are present. Begin with learning-rate candidates 0.0001 and 0.001 for small heads, and 0.00001 and 0.00003 for backbone adaptation; these are starting search values. Choose batch size from the actual memory smoke test, and log effective batch size and accumulation. Freeze model selection criteria before final replication.

Fit uncalibrated, temperature-scaled and regularised sigmoid alternatives on the calibration partition after predictor and selector choice. Use development validation to lock operating thresholds targeting 50%, 70%, 80% and 90% informative coverage. The nominal primary point is 80%. No arbitrary per-class isotonic switch is retained. Temperature scaling is established prior art. [15]

Conformal methods are optional secondary analyses with their loss, exchangeability assumptions, grouping and calibration allocation stated explicitly. Marginal prediction-set coverage is not an error bound among answered claims. A new calibration/selection design may be required for a formal result; do not quietly reuse a probability-calibration set as proof of every guarantee. [16]

# 11. Endpoints, statistical analysis and success criteria

### Primary empirical endpoint

At the frozen 80%-targeted validation operating point, measure **unsupported-assertion rate among informative focal claims**, decomposed into contradicted and unverifiable components. Measure **informative coverage** on all eligible records as the paired constraint. Abstention is not scored as an erroneous assertion, but it reduces coverage; zero answered claims produce an undefined risk, not zero risk.

Within each domain, give each independent acquisition group equal total weight and divide that weight over its eligible records. Report meal and packaged-product results separately. The registered combined analysis uses a 60:40 study mixture; it is not claimed to estimate population prevalence. Let w_i be these weights, a_i the indicator of an informative answer, and u_i indicate contradiction or unverifiability:

**U = sum(w_i × a_i × u_i) / sum(w_i × a_i).**  
**C = sum(w_i × a_i) / sum(w_i).**

Do not treat all claims from the same image or repeated views as independent cases. Record-level and group-level counts accompany every result.

**Primary decision rule:** claim improvement only when the paired 95% interval for U(M7) − U(M3) is entirely below zero AND the lower 95% bound for C(M7) − C(M3) is greater than −0.05. The five-percentage-point coverage margin is a proposed practical comparison tolerance requiring pilot-stage review, not a medical safety standard. Both conditions must pass. Report the two estimates even when the combined criterion fails.

Question budget is zero for the primary contrast. In the key secondary M8 experiment, all methods share an at-most-one-action budget; report actual actions and user time. Test equal-cost operating points or present the utility–cost frontier. Do not compare unconstrained interrogation with a zero-question baseline as a fair algorithmic test.

### Secondary outcomes

Report supported-claim yield per eligible record; omitted supported attributes; specificity distribution; food and complete-record precision/recall/F1; macro and support-weighted results; Brier score and log loss; calibration plots; risk–coverage curves; item-binding failures; false reassurance and unwarranted alarm under the registered rubric; and subgroup/domain estimates with support counts. Generic educational cards are evaluated for source fidelity, not counted as extra predictions to dilute assertion error.

When training against expert endorsement fractions, distinguish the soft-label target from a verified physical fact. For agreement calibration, retain annotator-level scoring and report label dispersion; do not quietly interpret majority vote as laboratory truth.

### Confidence intervals and replication

Use 1,000 paired bootstrap resamples of independent groups, preserving all linked records, claims and methods within a resample. Average the registered metric over seeds within each resample; report seed dispersion separately. Do not pool five seeds as five independent cohorts. Use sensitivity analyses for influential groups and sparse strata. Report an unstable or undefined interval honestly when there is insufficient support.

Keep one primary method contrast; prespecify secondary families and use a Holm adjustment within the designated confirmatory secondary family. Exploratory comparisons are labelled exploratory, including model- or subgroup-selected discoveries. Report intervals and effect sizes rather than using significance as the entire interpretation.

Risk–coverage plots are descriptive over the common feasible coverage range. Thresholds for the deployed policy come from development, not the test labels. No interpolation beyond achievable coverage is used to manufacture an operating point.

### Honest null outcomes

PCSI may not beat a well-calibrated joint-record predictor. Additional metadata may provide most of the benefit. Clarification may impose excessive burden. External performance may deteriorate. Such outcomes constrain the claim and the app; they do not justify replacing the target, hiding a seed or retuning on the test set. A substantial benchmark/failure-analysis paper remains possible, but publication quality is not guaranteed by the plan.

# 12. Robustness, external validity and security tests

Use prespecified tests for viewpoint, lighting, blur, partial occlusion, modest compression and unfamiliar presentation. Perturbations must not remove an item while retaining a label that presumes it remains visible. Record whether each test changes image quality, available information or the underlying reference scope.

Test missing, stale, incorrect and conflicting metadata separately. Construct product lookup failures and changed formulations; record the source snapshot so results can be reproduced. An exact product lookup may legitimately help the app, but evaluate held-out product families separately to measure generalisation beyond memorised packages.

Probe cross-item method swaps, deletion of a required source, contradiction between label and user answer, and unsupported certainty in generated wording. Test the evidence engine against incorrectly retrieved passages and absent source IDs. Reject or quarantine instructions embedded in package text or external documents; these are data, not commands to the app. The response renderer should accept only approved claim objects and cited evidence versions.

For vision-language models, use date-stamped new records to reduce known benchmark contamination, while acknowledging that training-data overlap cannot generally be ruled out for external models. Freeze prompt templates, decoding settings and model identifiers. Log API access and version drift without exposing participant data to unapproved services.

External success requires both accurate claims and useful coverage. Report failures by cuisine descriptor, acquisition setting, camera quality, food complexity and evidence availability without inferring protected personal attributes from images. Strata with few independent groups receive descriptive results rather than confident fairness claims.

# 13. Work packages and dependency schedule

The following is a planning allocation for the research team, not a promised delivery date or a claim that approvals, collaborators or funding exist. Week 1 starts when the supervisor authorises the amended programme. Human collection additionally waits for the required ethics and privacy decisions. Delayed gates move the dependent work; do not bypass them to preserve the calendar.

| Package | Planning window | Main output | Accountable role |
|---|---|---|---|
| WP0: amendment and decision record | Now, before execution | Target, scope and approval request | Anas; supervisor decision |
| WP1: evidence and claim protocol | Weeks 1–2 | Claim dictionary, evidence pack and preregistration skeleton | Anas + domain reviewer |
| WP2: rights, ethics and resources | Weeks 1–4 | Approved collection/storage and rights matrix | Supervisor + institutional support |
| WP3: public-data foundation | Weeks 2–5 | Audit, splits and reproducible seed-0 baselines | Anas |
| WP4: 100-record pilot | Weeks 3–6, after approval | Tested schema, annotation timing and power inputs | Collection/annotation team |
| WP5: main acquisition | Weeks 6–12 | Documented meal/product records | Collection lead |
| WP6: annotation and leakage lock | Weeks 6–14 | Reviewed records, frozen groups/splits | Reviewers + data steward |
| WP7: method development | Weeks 9–16 | PCSI, comparators, OOF selectors and unit tests | Anas + supervisor |
| WP8: full replication | Weeks 14–20 | Registered runs, calibration and analysis lock | Anas |
| WP9: prospective/external testing | Weeks 18–23, after lock | New-cohort evaluation and uncertainty estimates | Independent evaluator |
| WP10: paper and reproducibility | Weeks 22–26 | Manuscript, evidence tables and release audit | Authors, roles to agree |
| WP11: app research prototype | Weeks 20–26 | Product/meal modes and device evaluation | App/ML engineering |
| WP12: user evaluation | Weeks 26–30, after separate approval | Comprehension and burden study | User-study lead + domain reviewer |
| WP-L: laboratory feasibility | Parallel, separately funded | Assay feasibility and independent protocol | Analytical food-science partner |

These windows overlap deliberately, but the main dataset reference and test allocation must be locked before confirmatory analysis. The prospective cohort cannot become another tuning set. Model engineering may use already authorised public data while a new-data application is pending, provided the original supervisor execution gate has been cleared.

**Critical path:** target/claims → permissions and pilot → sufficient independent reference data → leakage-safe splits → comparators and method → calibration/analysis lock → prospective test → paper conclusions → validated app claims.

# 14. What to do first, in order

**Action 1 — adopt the amendment record.** Save this master plan beside the older files. Mark the four-tier target and `utils/oncoplate_proxy.py` as archival. Do not run the old proxy-label notebook as a source of active labels. Record that the programme owner accepts new data, heavier experiments and an app pathway; supervisor and institutional approvals remain separate.

**Action 2 — prepare the supervisor decision packet.** Include the one-page purpose, research questions, claim schema, pilot design, rights split, requested collaborators and the specific approval decision needed. Do not ask the user to reconfirm the already accepted direction. Obtain an actual supervisor decision before implementing the new scaffold/notebooks. [S1]

**Action 3 — resolve the scarce resources.** Seek a nutrition/food-science reviewer, two trained record annotators with adjudication coverage, an independent test custodian where feasible, and institutional advice on ethics, data rights and potential product ownership. Lab collaborators are optional. Record confirmed capacity, not just names of possible contacts.

**Action 4 — use the planning templates to finalise collection.** Fill the claim dictionary and pilot manifest specification, check the source ledger, and estimate annotation effort. Keep source facts and user-visible evidence distinct from sealed reference fields.

**Action 5 — after the execution gate, implement notebooks 00–05.** Verify environment, authorised downloads, actual annotation schema, duplicate graph, split integrity and a 256-image fitting-partition smoke test. Use the existing repository location; do not assume this document has altered it.

**Action 6 — obtain the first baseline package.** Run ResNet-50 seed 0 attribute and complete-record baselines. Save dataset audit, target specification, split integrity, environment lock, validation predictions and metrics. The milestone is a trustworthy pipeline, not a high headline score.

**Action 7 — execute the approved pilot in parallel with baseline development.** Measure reference completeness, reviewer agreement, question availability, group structure, annotation time and collection diversity. Refine the scope only from pilot/development evidence and document the changes.

**Action 8 — lock v3.1 before scale-up.** Finalise sample-size simulation, exact claim menu, primary task mixture, margin/precision targets, action policy, permissible data rights and the experiment matrix. Then expand collection and start the main method comparison.

# 15. Repository and notebook implementation map

Retain the recorded repository **`anasbiswas1/oncoplate-research`** and working path **`/content/drive/MyDrive/OncoPlate_Research/oncoplate-research/`**. Their current contents have not been inspected or modified for this deliverable. [S1, Section 9]

Place private raw data, contact records, source snapshots and restricted feature caches outside the public code tree. Use the repository for code, schemas, configs, redacted aggregate results and documentation only after rights review. Do not push raw labels or model artefacts automatically simply because a notebook finishes.

| Notebook / module to implement | Purpose | Required output |
|---|---|---|
| 00_environment_and_permissions | Paths, environment, recorded execution/data gates | environment manifest; gate report |
| 01_public_dataset_audit | FoodNExTDB schema and duplication checks | image/annotation manifests; audit |
| 02_claims_and_reference_schema | Validate attribute, claim and provenance structures | schema tests; target dictionary |
| 03_group_graph_and_splits | Leakage components and fixed allocations | split IDs; hashes; integrity report |
| 04_feature_smoke_test | Frozen ResNet extraction on fitting-only subset | reproducible feature cache |
| 05_seed0_baselines | Frequency, independent and joint heads | validation logits and metrics |
| 06_pilot_quality_and_precision | Pilot annotation, costs and sample simulation | pilot report; revised design |
| 07_new_benchmark_ingestion | New record imports and masks | versioned benchmark manifests |
| 08_frozen_and_finetuned_grid | Three backbones, two heads/regimes, five seeds | checkpoints; fit registry |
| 09_oof_selector_training | Grouped OOF predictions and matched selectors | OOF ledger; selector models |
| 10_source_gate_and_ablations | PCSI and deterministic tests | assertion audit; ablation results |
| 11_clarification_replay | Equal-budget information acquisition | episode trajectories; cost results |
| 12_calibration_and_lock | Calibration and frozen policies | calibration artefacts; analysis lock |
| 13_sealed_and_external_test | Execute locked evaluation once | protected predictions; test manifest |
| 14_grouped_statistics | Paired intervals, curves and robustness | registered result tables |
| 15_mobile_export_and_retest | Compression, export and device checks | export parity; mobile model card |
| 16_user_study_analysis | Approved comprehension evaluation | anonymised analysis; limitations |
| 17_paper_reproduction | Regenerate tables/figures from saved outputs | clean reproduction report |
| L01_assay_pilot, optional | Separate specimen/assay quality checks | lab provenance and pilot analysis |

The planning pack supplies this map and configuration contracts, not empty notebooks labelled as complete. Training code, models, approvals, data collection and app development remain to be executed.

# 16. Acceptance gates, resource plan and risk register

### Gates

**G0 — scientific scope:** owner acceptance recorded; supervisor decision documented; retired target removed from active specifications. **G1 — data authority:** each source has rights, storage and permitted-use entries; collection/participant approvals documented as required. **G2 — pilot readiness:** reference rubric, source masks, annotation burden and leakage grouping work on real pilot records. **G3 — analysis lock:** all models, thresholds, primary comparisons, exclusions and statistical rules are frozen before test access. **G4 — evidence:** results are reported regardless of direction; no unsupported guarantee or model-selected headline. **G5 — prototype:** lineage cleared, response tests pass, critical unsafe wording fixed, privacy/security review complete. **G6 — public release:** documented intended-purpose/regulatory decision, product-rights clearance, user evidence and incident process; paper acceptance alone does not pass this gate.

The specific human-facing risk tolerances must be reviewed before the user study or public release. The research comparison's 80% coverage target and five-point non-inferiority margin are not release-safety standards. Do not invent a clinical safety threshold from a convenient performance result.

### People and resources

Anas leads engineering and reproducibility. The existing plan names A. Mohasseb for supervisor review; additional responsibilities require agreement rather than assumption. A domain reviewer owns evidence interpretation, trained reviewers own record construction, and a test custodian protects evaluation data. Authorship is agreed according to actual contributions, not assigned by this work plan.

Prioritise annotation and verified records before a larger GPU tournament. Existing hardware can support smoke tests; actual memory, storage and adaptation feasibility must be measured. Cache frozen features and batch non-sensitive inference. Record GPU hours, paid API calls, storage and human-review effort. No current vendor prices or funded budget are assumed.

**Illustrative annotation workload, not a quote:** at 12 minutes per record per independent main/external review, 2,800 records × two passes requires 1,120 reviewer-hours, before adjudication, claim-output rating and collection. A 100-record three-review pilot at 15 minutes per review adds 75 hours. Pilot timing must replace these assumptions. This is a multi-person data project, not only a GPU project.

Budget fields: collection hours; food/product procurement; reviewer hours and rate; adjudication; domain review; compute hours and rate; API requests and rate; storage; participant compensation; app/device testing; legal/rights support; optional specimen and assay costs. Obtain written institutional resource decisions before expanding commitments. An unfilled budget is not an approved zero-cost plan.

### Major risks and prescribed responses

| Risk | Early indicator | Response |
|---|---|---|
| No domain reviewer | Claim definitions remain disputed | Continue authorised engineering only; do not freeze dietary assertions |
| Annotation cost exceeds capacity | Pilot timing exceeds allocation | Rebudget or reduce secondary breadth before reducing reference quality |
| Group support too small | Many images share a few sources | Recruit new groups, not more duplicate views |
| No advantage over strong baseline | Paired interval includes no improvement | Report null/failure analysis; do not manufacture novelty |
| Source gate abstains excessively | Low useful coverage | Diagnose missing inputs; report limits; do not relabel unknown facts |
| App lineage includes restricted data | Rights ledger cannot clear a checkpoint | Retrain on approved assets or seek permission; do not launder via distillation |
| Users read uncertainty as safety | Misinterpretation in approved study | Revise wording, retest, and withhold release |
| Laboratory relationship absent | No validated measurement protocol | Defer chemistry; retain the core information study |

# 17. Paper deliverables and reporting strategy

The main paper should tell one coherent story: identify the information failure; define the benchmark and reference; implement a source-aware intervention; compare it fairly; test generalisation; explain what can and cannot become an app claim.

**Required evidence package:** dataset flow and group counts; class/claim and source-support tables; reviewer agreement; licence and provenance summary; baseline and ablation results; risk–coverage and usefulness curves; calibration analysis; prospective/external comparisons; question burden; confidence intervals; error examples chosen by a reproducible procedure; computational cost; limitations and access instructions.

**Proposed main exhibits:** (1) system/data architecture; (2) benchmark collection and source-availability map; (3) unsupported claims by failure mode; (4) paired risk–coverage comparison; (5) clarification gain versus cost; (6) external-domain and subgroup results; (7) compression and export-parity results. Tables include the reference taxonomy, primary paired contrast, ablations and independent-group counts. Figures are generated from saved results, not manually invented numbers.

Freeze the contribution statement to what the results support. Do not claim first-ever status, chemical detection, reduced cancer incidence or general clinical safety. Do not describe a simulator or API call as a user trial. An integrated benchmark/method paper does not intrinsically require a wet lab, but any chemical-concentration claim requires an appropriate measured reference.

Choose the journal after reviewing actual methods, validation depth, article scope and current author instructions. No quartile, acceptance probability, journal suitability guarantee or APC assumption is made here. Separate later app-impact and chemistry papers only when they have distinct questions, new evidence and transparent reuse of the common system.

# 18. Mobile-app roadmap and product lineage

### Prototype A — product-information mode

Capture a barcode or ingredient-panel photograph; confirm the exact product/formulation when possible; record lookup date and source; identify the relevant attributes; display an evidence-linked card and uncertainty; allow correction or “I do not know”. A database hit is not proof that the package is the same formulation. The mobile extraction component must be separately evaluated for text errors; the reference panel is human-reviewed.

### Prototype B — meal mode

Capture the meal; identify multiple components and their associations; show qualified interpretations; request only useful missing information; separate assertions from general evidence. Limit the first interface to approved templates. Free-form generation is optional and must pass fidelity checks against the selected claim objects before display.

### Prototype C — logged patterns, later

Record confirmed items, quantities and log completeness before summarising intake. WCRF's red/processed-meat guidance is a source of reviewed general information, not a personalised risk formula; exact recommendations and raw/cooked units must be versioned. [2] Incomplete logs cannot justify a complete-week assessment. No gamified cancer score or implicit “safe allowance” should be shown.

### Engineering and safety contract

Use a platform-neutral inference interface first, with fields for record ID, input mode, claim ID, value, qualifier, support score, required sources, missing fields, conflict flags, evidence version and model hash. Keep health profiles out of the initial app where unnecessary. Default to minimal retention and explicit permission for any uploaded photographs. Separate researcher/admin functions from participant views.

For export, compare server and device outputs on the same locked cases; test unsupported-claim risk, coverage, calibration and binding errors after quantisation or distillation. Measure latency distributions, peak memory, battery/thermal behaviour where feasible, offline operation and timeouts on declared device classes. A compressed model is a new evaluated artefact, not automatically equivalent to the research checkpoint.

**Rights firewall.** FoodNExTDB restricts commercial use, including extracted features. Keep its research lineage separate. Do not assume fine-tuning, synthetic labels or teacher–student distillation removes the underlying obligations; obtain permission or an institutional legal determination before relying on affected artefacts in a product. [4] The source registry must cover every dataset, checkpoint, derived label, cache and product lookup used for a release.

Nutrition5k states share/adapt permission including commercial purposes, while Open Food Facts distinguishes database, content and image licences. Review exact attribution, share-alike and reuse obligations for the implementation; a permissive code licence does not settle the rights of all data or weights. [6,7]

# 19. Prospective and human-facing evaluation

Keep two distinct studies. The 400-record prospective/external cohort evaluates a frozen inference procedure on fresh documented inputs. A separate user study evaluates whether people understand and use the output appropriately. Recruitment, consent and any risk-management requirements are handled through the approved institutional process.

Begin with approximately 15–20 formative participants to identify misunderstandings and usability problems. After revising and freezing the interface, plan a controlled study with an initial allocation of 80 participants, 40 per arm, subject to pilot-based precision and ethics review. Do not count formative participants as an independent confirmatory cohort.

Compare the same underlying predictions and evidence in two interfaces: a minimal calibrated information display and the source-aware display with explicit missing-premise explanations. Where studying the integrated clarification feature instead, describe the comparison as a whole-system effect and report the extra interaction time. Randomise assignment and balance case difficulty; avoid exposing each participant to the same case under both interfaces unless carry-over is designed and analysed.

Primary user outcomes are comprehension of supported versus unknown information and appropriate reliance on correct/incorrect suggestions. Secondary outcomes include unnecessary alarm, inappropriate reassurance, completion burden and usability. Do not maximise subjective trust as a goal: appropriate scepticism is desirable. Neither this study nor the model evaluation measures reduced cancer incidence.

General-adult educational testing is not a clinical trial in cancer patients. Exclude treatment recommendations from the protocol. Any future study involving clinical populations or behaviour change as a health intervention needs its own design, expertise and approvals.

**Regulatory/privacy checkpoint.** MHRA guidance connects intended purpose to functionality, instructions and promotional claims; a disclaimer alone does not settle classification. Obtain a documented assessment before public release. [17] ICO guidance identifies health-related personal information and some inferred profiles as special-category data; it currently notes that guidance is under review following legislative change. Obtain institutional advice on the applicable lawful basis, special-category condition where needed, retention, transfers and participant rights at the time of collection. [18]

# 20. Optional laboratory extension and programme close-out

The laboratory work asks a separate question: can images and recorded preparation predict concentrations of specified compounds under a validated analytical method? It does not retrospectively turn all visual labels into chemical measurements. NCI describes different formation mechanisms and determinants for HCAs and PAHs and notes the limitations of human evidence linking cooked-meat exposure to cancer. [3]

Start with a qualified analytical food-science partner selecting a justified small analyte panel and suitable food matrices. Plan a 30–50-specimen assay feasibility study before budgeting a larger 150–300-portion experiment. These are provisional workload ranges, not powered sample-size claims. Include limits of detection/quantification, recoveries, blanks, reference materials where available, batch effects and censored observations in the protocol. Laboratory preparation and analysis follow the partner's approved procedures.

Pair images and preparation logs with measurements from the same specimen. Compare image-only, preparation-only and combined predictors, with independent preparation batches, ingredient lots and appliances held out. Technical assay replicates and repeated photographs do not create independent specimens. External laboratory validation is desirable before a public measurement feature.

A valid negative outcome is that image appearance adds little to preparation information. A sensor-assisted phone reader is a different product path requiring its own sensor validation and rights review; it is not equivalent to passive plate-image chemistry. No concentration threshold should be presented as an individual cancer-risk boundary without appropriate external evidence.

**Definition of successful programme completion:** an honest, reproducible paper with a valid reference standard; a documented account of which information the method can support; an evaluated prototype restricted to those capabilities; and a transparent decision about whether chemistry or broader deployment is justified. Success is not a promised journal tier, universal food-safety verdict or cancer-prevention claim.

---

# References and source-verification notes

**[S1] Supplied source:** *OncoPlate Stage 0 Research Plan*, v1.2, June 2026 with September corrections. The primary tier target is retired in its banner; execution gate in line 13; deployment-only inputs in lines 109–113; grouping/seeds in lines 158–175; repository in line 181; unresolved domain review in lines 239–245.

**[S2] Supplied companion and conversation:** *OncoPlate Stage 0 v1.3 Experiment Runbook* and the user's acceptance, on 18 September 2026, of the expanded research-to-app direction. The complete runbook has not been re-audited here; its earlier baseline sequence is retained only where explicitly restated in this plan. No source proposal, approval or experimental result is inferred from an earlier assistant's assertion alone.

[1] World Health Organization. *Cancer: Carcinogenicity of the consumption of red meat and processed meat*. Official question-and-answer page. https://www.who.int/news-room/questions-and-answers/item/cancer-carcinogenicity-of-the-consumption-of-red-meat-and-processed-meat/ . Checked 18 September 2026; relevant official text inspected.

[2] World Cancer Research Fund. *Limit consumption of red and processed meat*. https://www.wcrf.org/research-policy/evidence-for-our-recommendations/limit-red-processed-meat/ . Checked 18 September 2026; recommendation and evidence wording inspected.

[3] National Cancer Institute. *Chemicals in Meat Cooked at High Temperatures and Cancer Risk*. https://www.cancer.gov/about-cancer/causes-prevention/risk/diet/cooked-meats-fact-sheet . Checked 18 September 2026; mechanisms and limitations inspected.

[4] AI4Food. *FoodNExTDB repository*. https://github.com/AI4Food/FoodNExtDB . Checked 18 September 2026; README and research-use restriction inspected. Dataset archive not downloaded or audited for this work plan.

[5] *Are Vision-Language Models Ready for Dietary Assessment? Exploring the Next Frontier in AI-Powered Food Image Recognition*. arXiv:2504.06925. https://arxiv.org/html/2504.06925v1 . Checked 18 September 2026; relevant HTML text inspected, not an experimental reproduction.

[6] Google Research Datasets. *Nutrition5k*. https://github.com/google-research-datasets/Nutrition5k . Checked 18 September 2026; ingredients, grouping and stated reuse permission inspected. Archive not downloaded.

[7] Open Food Facts. *License — be on the legal side*. https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/ . Checked 18 September 2026; licence distinctions inspected.

[8] Lee W, Mekkoth P, Tian Y, Gungor O, Rosing T. *FoodCHA: Multi-Modal LLM Agent for Fine-Grained Food Analysis*. arXiv:2605.05499, 2026. https://arxiv.org/html/2605.05499v1 . Checked 18 September 2026; record and relevant HTML inspected. Preprint status used in this plan.

[9] *OmniFood-Bench: Evaluating VLMs for Nutrient Reasoning and Personalized Health Advice*. arXiv:2607.08423, v2, 2026. https://arxiv.org/abs/2607.08423 . Checked 18 September 2026; abstract and version record inspected. Detailed implementation remains a development review task.

[10] Li Z, Yan C, Jackson NJ, Cui W, Li B, Zhang J, Malin BA. *Towards Statistical Factuality Guarantee for Large Vision-Language Models*. EMNLP 2025, 11435–11456. DOI: 10.18653/v1/2025.emnlp-main.576. https://aclanthology.org/2025.emnlp-main.576/ . Checked 18 September 2026; publisher metadata and abstract inspected. Formal adaptation requires full-method review.

[11] Xu J, Wu Y, Zeng D, Paisley J, Zhao Q. *Look Again Before You Abstain: Budgeted Conformal Evidence Acquisition for Reliable Vision-Language Model*. arXiv:2606.16667, v4, 2026. https://arxiv.org/abs/2606.16667 . Checked 18 September 2026; abstract and version record inspected; no guarantee reproduced.

[12] Goren S, Galil I, El-Yaniv R. *Hierarchical Selective Classification*. arXiv:2405.11533, v2. https://arxiv.org/abs/2405.11533 . Checked 18 September 2026; record/abstract inspected.

[13] Khurana U, Nalisnick E, Fokkens A, Swayamdipta S. *Crowd-Calibrator: Can Annotator Disagreement Inform Calibration in Subjective Tasks?* arXiv:2408.14141; record states accepted at COLM 2024. https://arxiv.org/abs/2408.14141 . Checked 18 September 2026; record/abstract inspected.

[14] *When and why vision-language models behave like bags-of-words, and what to do about it?* arXiv:2210.01936. https://arxiv.org/abs/2210.01936 . Checked 18 September 2026; record/abstract inspected. Used for attribute-binding precedent, not dietary validity.

[15] Guo C, Pleiss G, Sun Y, Weinberger KQ. *On Calibration of Modern Neural Networks*. ICML 2017, PMLR 70:1321–1330. https://proceedings.mlr.press/v70/guo17a . Checked 18 September 2026; proceedings record and abstract inspected.

[16] Lee Y, Foygel Barber R, Willett R. *Distribution-free inference with hierarchical data*. arXiv:2306.06342, v4. https://arxiv.org/abs/2306.06342 . Checked 18 September 2026; record/abstract inspected. No theorem is claimed for PCSI on this basis alone.

[17] Medicines and Healthcare products Regulatory Agency. *Crafting an intended purpose in the context of software as a medical device*. https://www.gov.uk/government/publications/crafting-an-intended-purpose-in-the-context-of-software-as-a-medical-device-samd/crafting-an-intended-purpose-in-the-context-of-software-as-a-medical-device-samd . Checked 18 September 2026; relevant official guidance inspected, not a legal classification of OncoPlate.

[18] Information Commissioner's Office. *What is special category data?* https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/ . Checked 18 September 2026; health/inference text and update warning inspected. Obtain current institutional advice at collection and release.

[19] TorchVision. *resnet50*. https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html . Checked 18 September 2026; official model documentation inspected. Pin installed software and weights at execution.

[20] TorchVision. *convnext_tiny*. https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.convnext_tiny.html . Checked 18 September 2026; official model documentation inspected. This is not ConvNeXt-V2.

[21] Meta / FAIR. *DINOv2 repository*. https://github.com/facebookresearch/dinov2 . Checked 18 September 2026; checkpoint interface and repository inspected. Review the exact weight licence; different model extensions have different terms.

**What has actually been completed for this deliverable:** the upgraded work plan, refreshed source checks described above, and planning templates. **Not completed:** supervisor/ethics approval; dataset archive or user-repository audit; pilot collection; model training; sample-size simulation; laboratory validation; mobile implementation; or proof of priority. Original supplied files remain unchanged.
