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

## Notebook 27: base-rate initialised heads (seed 0, amendment ba0ce10)
Amendment: TrainSpec.bias_init = "prior" zeroes the output layer weights and sets each output
bias to the fit-partition base-rate log-odds, so the untrained head reproduces the frequency
baseline. Same learning rates and 400-epoch cap as notebook 26. All six runs ended by early
stopping after 12 to 15 epochs. Runs are under runs/foundation_prior_init/. Under the amended
code, notebook 05 runs are incompatible with the principal grid and are re-run before notebook 08.

### Validation, identical records
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1731 | 0.0055 | 0.503 |
| Independent | Base rate, lr 0.001, stopped at 14 | 0.1263 | 0.0125 | 0.797 |
| Independent | Base rate, lr 0.003, stopped at 12 | 0.1312 | 0.0156 | 0.802 |
| Independent | Base rate, lr 0.01, stopped at 12 | 0.1611 | 0.0232 | 0.782 |
| Joint | Frequency baseline (no image) | 0.0329 | 0.0009 | 0.225 |
| Joint | Base rate, lr 0.001, stopped at 13 | 0.0266 | 0.0025 | 0.455 |
| Joint | Base rate, lr 0.003, stopped at 13 | 0.0277 | 0.0025 | 0.454 |
| Joint | Base rate, lr 0.01, stopped at 15 | 0.0369 | 0.0047 | 0.383 |

### Calibration partition, selected configuration, reported once
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1674 | 0.0043 | 0.467 |
| Independent | Base rate, lr 0.001, stopped at 14 | 0.1231 | 0.0133 | 0.798 |
| Joint | Frequency baseline (no image) | 0.0318 | 0.0005 | 0.213 |
| Joint | Base rate, lr 0.001, stopped at 13 | 0.0258 | 0.0026 | 0.478 |

Both base-rate heads have lower log-loss and higher top-1 endorsement than the frequency
baseline on validation and on the calibration partition. Single seed; no intervals computed.
The frequency baseline's near-zero ECE comes from a constant prediction at the base rate,
which is calibrated by construction and carries no per-image information. The notebook 21
calibration and test-set figures were measured on default-initialised heads and do not
describe these heads.

## Notebook 28: calibration and selective prediction on base-rate heads (seed 0)
Selected runs: learning rate 0.001 for both heads (notebook 27). Calibrators fitted on the
calibration partition (1938 records) and compared on validation (992 records). Intervals are
participant-group bootstrap, 1000 replicates, every calibrator scored on the same draw.
Test records are not read.

### Validation
| Head | Calibrator | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1731 | 0.0055 | 0.503 |
| Independent | Uncalibrated | 0.1263 | 0.0125 | 0.797 |
| Independent | Temperature (T = 0.873) | 0.1246 | 0.0045 | 0.797 |
| Independent | Sigmoid, per label | 0.1239 | 0.0040 | 0.794 |
| Joint | Frequency baseline (no image) | 0.0329 | 0.0009 | 0.225 |
| Joint | Uncalibrated | 0.0266 | 0.0025 | 0.455 |
| Joint | Temperature (T = 0.895) | 0.0261 | 0.0005 | 0.455 |
| Joint | Sigmoid, per label | 0.0261 | 0.0008 | 0.470 |

### Change against uncalibrated, 95% interval
| Head | Calibrator | Log-loss change | ECE change |
|---|---|---|---|
| Independent | Temperature | -0.0017 [-0.0033, -0.0002] | -0.0080 [-0.0085, -0.0019] |
| Independent | Sigmoid | -0.0025 [-0.0051, 0.0004] | -0.0085 [-0.0122, 0.0004] |
| Joint | Temperature | -0.0005 [-0.0008, -0.0001] | -0.0020 [-0.0024, -0.0007] |
| Joint | Sigmoid | -0.0005 [-0.0011, 0.0001] | -0.0017 [-0.0024, -0.0002] |

### Selective prediction, validation: panel disagreement among assessable answers
| Head | Coverage | Uncalibrated and temperature | Sigmoid |
|---|---|---|---|
| Independent | 100% | 0.203 [0.145, 0.267] | 0.206 [0.153, 0.256] |
| Independent | 80% | 0.140 [0.095, 0.193] | 0.152 [0.104, 0.202] |
| Independent | 50% | 0.090 [0.048, 0.139] | 0.090 [0.055, 0.127] |
| Joint | 100% | 0.545 [0.493, 0.598] | 0.530 [0.480, 0.584] |
| Joint | 80% | 0.469 [0.410, 0.528] | 0.455 [0.399, 0.511] |
| Joint | 50% | 0.340 [0.284, 0.396] | 0.343 [0.288, 0.399] |

Temperatures below 1 show the uncalibrated heads are slightly under-confident. A single
temperature cannot change the chosen label or the confidence ordering, so its selective rows
equal the uncalibrated rows. Intervals at different coverages come from the same records and
are not a test of the change between coverages. ECE intervals are less reliable than log-loss
intervals. Single seed; validation was also used for early stopping and learning-rate selection.
ResNet-50 frozen is a control model in the accepted plan; the principal anchor is DINOv2.

## Notebook 29: DINOv2 frozen heads (seed 0)
DINOv2-small (dinov2_vits14, frozen CLS features), base-rate initialised heads, learning rates
0.001, 0.003 and 0.01, 400-epoch cap; all six runs ended by early stopping (13 to 43 epochs).
Learning rate 0.001 was selected for both heads by validation loss. Intervals are paired
participant-group bootstrap, 1000 replicates. Test records are not read.

### Validation, identical records
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1731 | 0.0055 | 0.503 |
| Independent | ResNet-50, lr 0.001 (notebook 27) | 0.1263 | 0.0125 | 0.797 |
| Independent | DINOv2, lr 0.001, stopped at 43 | 0.1058 | 0.0036 | 0.862 |
| Independent | DINOv2, lr 0.003, stopped at 19 | 0.1063 | 0.0048 | 0.853 |
| Independent | DINOv2, lr 0.01, stopped at 13 | 0.1094 | 0.0037 | 0.849 |
| Joint | Frequency baseline (no image) | 0.0329 | 0.0009 | 0.225 |
| Joint | ResNet-50, lr 0.001 (notebook 27) | 0.0266 | 0.0025 | 0.455 |
| Joint | DINOv2, lr 0.001, stopped at 43 | 0.0227 | 0.0009 | 0.594 |
| Joint | DINOv2, lr 0.003, stopped at 20 | 0.0228 | 0.0010 | 0.594 |
| Joint | DINOv2, lr 0.01, stopped at 13 | 0.0236 | 0.0013 | 0.569 |

### Calibration partition (neither backbone used it for selection)
| Head | Model | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Frequency baseline (no image) | 0.1674 | 0.0043 | 0.467 |
| Independent | ResNet-50, base-rate head | 0.1231 | 0.0133 | 0.798 |
| Independent | DINOv2, base-rate head | 0.1054 | 0.0046 | 0.848 |
| Joint | Frequency baseline (no image) | 0.0318 | 0.0005 | 0.213 |
| Joint | ResNet-50, base-rate head | 0.0258 | 0.0026 | 0.478 |
| Joint | DINOv2, base-rate head | 0.0226 | 0.0011 | 0.563 |

DINOv2 minus ResNet-50, 95% interval: independent log-loss -0.0177 [-0.0207, -0.0151],
top-1 +0.050 [+0.028, +0.072]; joint log-loss -0.0032 [-0.0036, -0.0029],
top-1 +0.085 [+0.067, +0.104]. All four intervals exclude zero.

### Calibration of the selected DINOv2 heads, validation
| Head | Calibrator | Log-loss | ECE | Top-1 |
|---|---|---|---|---|
| Independent | Uncalibrated | 0.10582 | 0.0036 | 0.862 |
| Independent | Temperature (T = 0.962) | 0.10568 | 0.0031 | 0.862 |
| Independent | Sigmoid, per label | 0.10591 | 0.0032 | 0.869 |
| Joint | Uncalibrated | 0.02274 | 0.0009 | 0.594 |
| Joint | Temperature (T = 0.954) | 0.02268 | 0.0004 | 0.594 |
| Joint | Sigmoid, per label | 0.02274 | 0.0004 | 0.586 |

Change against uncalibrated, 95% interval:
| Head | Calibrator | Log-loss change | ECE change |
|---|---|---|---|
| Independent | Temperature | -0.000149 [-0.000545, 0.000263] | -0.000529 [-0.001810, 0.001564] |
| Independent | Sigmoid | 0.000083 [-0.000762, 0.000977] | -0.000359 [-0.003185, 0.003494] |
| Joint | Temperature | -0.000065 [-0.000194, 0.000071] | -0.000472 [-0.000731, 0.000546] |
| Joint | Sigmoid | -0.000008 [-0.000196, 0.000200] | -0.000424 [-0.000815, 0.000838] |

None of the eight intervals excludes zero. Temperatures near 1 show the DINOv2 heads are
close to calibrated without post-hoc correction; the ResNet-50 heads (notebook 28) had
temperatures of 0.873 and 0.895 and small gains whose intervals excluded zero.

### Selective prediction, validation: panel disagreement among assessable answers
| Head | Coverage | Uncalibrated and temperature | Sigmoid |
|---|---|---|---|
| Independent | 100% | 0.138 [0.095, 0.186] | 0.131 [0.094, 0.173] |
| Independent | 80% | 0.073 [0.043, 0.111] | 0.071 [0.041, 0.110] |
| Independent | 50% | 0.023 [0.007, 0.045] | 0.028 [0.010, 0.050] |
| Joint | 100% | 0.406 [0.348, 0.468] | 0.414 [0.360, 0.474] |
| Joint | 80% | 0.326 [0.273, 0.380] | 0.330 [0.276, 0.383] |
| Joint | 50% | 0.191 [0.154, 0.228] | 0.198 [0.159, 0.236] |

Intervals at different coverages come from the same records and are not a test of the change
between coverages. Single seed; frozen features; validation was also used for early stopping
and learning-rate selection. The accepted plan's principal anchor is DINOv2 fine-tuned.
