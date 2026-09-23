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

## Notebook 26: convergence against the frequency baseline (seed 0)
ResNet-50 frozen heads retrained with learning rates 0.001, 0.003 and 0.01 and a 400-epoch cap.
All six runs ended by early stopping (patience 10), none at the cap. Runs are under
runs/foundation_convergence/; notebook 05 runs are unchanged. Top-1 endorsement is the
group-weighted mean panel endorsement of the highest-probability label, over records where
that label was observed, as in notebook 21.

### Validation, identical records
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1731 | 0.0055 | 0.503 |
| Independent | Notebook 05 (lr 0.001, cap 100) | 0.2249 | 0.0811 | 0.753 |
| Independent | lr 0.001, stopped at 152 | 0.2103 | 0.0475 | 0.745 |
| Independent | lr 0.003, stopped at 69 | 0.2099 | 0.0450 | 0.741 |
| Independent | lr 0.01, stopped at 28 | 0.2096 | 0.0466 | 0.747 |
| Joint | Frequency baseline (no image) | 0.0329 | 0.0009 | 0.225 |
| Joint | Notebook 05 (lr 0.001, cap 100) | 0.1105 | 0.0869 | 0.411 |
| Joint | lr 0.001, stopped at 307 | 0.0391 | 0.0053 | 0.390 |
| Joint | lr 0.003, stopped at 172 | 0.0398 | 0.0053 | 0.381 |
| Joint | lr 0.01, stopped at 63 | 0.0416 | 0.0097 | 0.398 |

### Calibration partition, selected configuration, reported once
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1674 | 0.0043 | 0.467 |
| Independent | lr 0.01, stopped at 28 | 0.2070 | 0.0494 | 0.739 |
| Joint | Frequency baseline (no image) | 0.0318 | 0.0005 | 0.213 |
| Joint | lr 0.001, stopped at 307 | 0.0374 | 0.0059 | 0.384 |

Neither converged head has lower log-loss than the frequency baseline on either partition.
Both have higher top-1 endorsement. Single seed; no intervals computed. The linear head's
output biases start near zero, i.e. probability about 0.5 per label.
