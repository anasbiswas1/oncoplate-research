# Foundation results log

## Correction to commit ae50844
The commit message reports "macro-F1 independent 0.173 / joint 0.033". Those values are the
frequency baseline's validation log-loss printed by notebook 05, not macro-F1 of the learned
models. Per-label precision, recall and F1 are saved in each run's validation_per_label.csv;
no macro average was reported.

## Validation log-loss, seed 0 (lower is better)

| Model | Independent (85 labels) | Joint (272 labels) |
|---|---|---|
| Frequency baseline (fit-partition prevalence, no image) | 0.1731 | 0.0329 |
| ResNet-50 frozen, uncalibrated | 0.2249 | 0.1105 |
| + temperature scaling (fit on calibration partition) | 0.2145 | 0.0371 |
| + sigmoid scaling (fit on calibration partition) | 0.1402 | 0.0310 |

Uncalibrated, the image models have higher log-loss than the no-image baseline on both heads.
Both runs stopped at the 100-epoch cap with validation loss still decreasing.

## Test-set selective analysis (notebook 21, under analysis_lock.json)
Panel disagreement at 0.80 target coverage used the temperature calibrator: independent 0.178,
joint 0.502. The frequency baseline is not evaluated on test, so these values have no
no-image reference.
