# Primary source and implementation register

The accepted master plan retains its scientific sources. This release additionally checked the following official technical interfaces. A checked README is not an audited archive or successful model download.

- Colab FAQ: https://research.google.com/colaboratory/faq.html — paid resources remain variable; use persistence and resumable workloads, not keep-alive bypasses.
- FoodNExTDB official repository: https://github.com/AI4Food/FoodNExtDB — CSV/image layout and research-only terms, including extracted features. Configured archive: https://bidalab.eps.uam.es/static/AI4FoodDB/FoodNExtDB.zip . The full archive was not downloaded in the packaging environment.
- ResNet-50: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html
- ConvNeXt-Tiny: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.convnext_tiny.html
- DINOv2 official implementation: https://github.com/facebookresearch/dinov2 ; checkpoint interface used here is facebook/dinov2-small in Transformers. The actual immutable weight snapshot is recorded at first execution.
- Qwen2.5-VL: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct and https://huggingface.co/docs/transformers/model_doc/qwen2_5_vl
- SmolVLM: https://huggingface.co/HuggingFaceTB/SmolVLM-Instruct and https://huggingface.co/docs/transformers/model_doc/smolvlm
- Nutrition5k: https://github.com/google-research-datasets/Nutrition5k — use only overlapping ingredient/mass tasks. The source README lists an ingredient-count field and seven named ingredient fields while referring to eight repeated fields. The parser therefore accepts only validated seven-field blocks with an optional matching explicit count and fails on other layouts. This is an explicit schema-compatibility accommodation, not invented food data. Incremental scans of the same plate must remain linked.
- Open Food Facts API documentation: https://openfoodfacts.github.io/openfoodfacts-server/api/ — the checked source identifies v3.6 as current and v2 as supported but deprecated. The read-only client defaults to v3.6, caches raw source snapshots and respects a conservative per-request delay. Rate limits can change: recheck them before large collections. No guarantee of record completeness or exact package-formulation match is assumed.

Dataset, code, model and product-image licences must each be reviewed. Preserve retrieval dates and exact source snapshots. Never cite an abstract as verification of an unseen implementation detail.
