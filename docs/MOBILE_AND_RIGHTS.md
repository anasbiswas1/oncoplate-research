# Mobile prototype and lineage

This repository supplies visual-model export, parity checks, a local research-only HTTP interface, mobile-responsive preview and a platform-neutral schema. It does not supply a released native mobile application, clinical validation, regulatory determination or universal cancer-food scanner.

The visual API deliberately accepts an image, not client-created “verified facts”. It reports record-presence model predictions and states that its probabilities are visual annotation probabilities, not cancer risk or independently calibrated claim support. The reviewed PCSI/renderer pipeline is available in the study modules, but a deployment service must resolve provenance server-side and undergo separate testing.

TorchScript export works without optional ONNX tools. ONNX is an opt-in compatibility path. Quantisation is supplied as a **head-only int8 ablation** for frozen-feature models; do not describe it as a fully int8 image backbone or as a complete phone conversion. Export parity is tested first on a tensor and then on held validation inputs. Device latency, thermal/battery behaviour and complete claim-policy parity need actual target-device measurement. Host timings are not phone measurements.

Keep data/checkpoint lineage as a directed graph: each derived asset names all parents and their permitted research/product uses. FoodNExTDB's research-only restriction is not removed by fine-tuning, pseudo-labels or distillation. The same applies to any other restricted parent. `check_lineage` rejects missing permissions, missing parents and cycles. It cannot replace legal review.

Before public release: reviewed intended purpose/claims; appropriate regulatory/privacy determination; institution and creator IP decisions; explicit data and model rights; trustworthy source handling; user comprehension and appropriate-reliance evidence; incident/correction process. An accepted paper alone is not release authorisation.
