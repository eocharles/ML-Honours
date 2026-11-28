All times are seconds of compute time (selection stage, median over repeats). Disagreement: lower = more stable; rank 1 = most stable. Same seeds, so the forests are identical for both explainers.

### breast_cancer (569 rows, 30 features)

- permutation: 3 repeat(s), complete
- tree: 3 repeat(s), complete

| candidate | trees | risk (Brier) | SHAP s (permutation) | stability s (permutation) | disagreement (permutation) | rank (permutation) | SHAP s (tree) | stability s (tree) | disagreement (tree) | rank (tree) | SHAP speed-up |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 588f99a921dd | 200 | 0.0468 | 1.26 | 1.60 | 0.109 | 5 | 0.02 | 0.37 | 0.080 | 2 | 63x |
| 93c3af789f62 | 400 | 0.0506 | 2.21 | 2.81 | 0.083 | 3 | 0.03 | 0.69 | 0.103 | 5 | 75x |
| 99c56a33fdd7 | 400 | 0.0406 | 2.20 | 2.85 | 0.148 | 6 | 0.03 | 0.71 | 0.112 | 6 | 64x |
| 30682ab8a273 | 600 | 0.0499 | 3.13 | 4.04 | 0.071 | 1 | 0.04 | 1.23 | 0.088 | 4 | 77x |
| d35d29df0546 | 600 | 0.0462 | 3.13 | 4.03 | 0.082 | 2 | 0.04 | 0.96 | 0.074 | 1 | 71x |
| df617ef7fa25 | 600 | 0.0410 | 3.15 | 4.06 | 0.109 | 4 | 0.04 | 1.00 | 0.085 | 3 | 70x |

**Selections**

| selector | permutation | tree | same? |
|---|---|---|---|
| risk_only | 99c56a33fdd7 | 99c56a33fdd7 | yes |
| stable_5pct | df617ef7fa25 | df617ef7fa25 | yes |
| knee | df617ef7fa25 | df617ef7fa25 | yes |

Stability ranking identical across explainers: False


### riccardo (20000 rows, 4296 features)

- permutation: 1 repeat(s), INCOMPLETE (1 of 6 candidates finished)
- tree: 1 repeat(s), complete

| candidate | trees | risk (Brier) | SHAP s (permutation) | stability s (permutation) | disagreement (permutation) | rank (permutation) | SHAP s (tree) | stability s (tree) | disagreement (tree) | rank (tree) | SHAP speed-up |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 588f99a921dd | 200 | 0.1610 | 4086.89 | 4105.59 | 0.707 | - | 0.17 | 16.47 | 0.653 | 6 | 24347x |
| 93c3af789f62 | 400 | 0.1145 | not run | not run | not run | - | 0.53 | 173.90 | 0.318 | 4 | - |
| 99c56a33fdd7 | 400 | 0.0719 | not run | not run | not run | - | 0.44 | 49.47 | 0.352 | 5 | - |
| 30682ab8a273 | 600 | 0.1144 | not run | not run | not run | - | 0.41 | 237.03 | 0.265 | 1 | - |
| d35d29df0546 | 600 | 0.0741 | not run | not run | not run | - | 0.53 | 75.92 | 0.285 | 2 | - |
| df617ef7fa25 | 600 | 0.1479 | not run | not run | not run | - | 0.25 | 143.43 | 0.303 | 3 | - |

**Selections**

| selector | permutation | tree | same? |
|---|---|---|---|
| risk_only | not finished | 99c56a33fdd7 | - |
| stable_5pct | not finished | d35d29df0546 | - |
| knee | not finished | d35d29df0546 | - |

Stability ranking identical across explainers: cannot tell yet (permutation incomplete)


### spambase (4601 rows, 57 features)

- permutation: 3 repeat(s), complete
- tree: 3 repeat(s), complete

| candidate | trees | risk (Brier) | SHAP s (permutation) | stability s (permutation) | disagreement (permutation) | rank (permutation) | SHAP s (tree) | stability s (tree) | disagreement (tree) | rank (tree) | SHAP speed-up |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 588f99a921dd | 200 | 0.0819 | 2.43 | 2.91 | 0.279 | 6 | 0.02 | 0.55 | 0.104 | 6 | 107x |
| 93c3af789f62 | 400 | 0.0651 | 4.28 | 5.47 | 0.239 | 5 | 0.05 | 1.27 | 0.057 | 2 | 84x |
| 99c56a33fdd7 | 400 | 0.0508 | 4.37 | 5.69 | 0.230 | 4 | 0.07 | 1.31 | 0.074 | 5 | 60x |
| 30682ab8a273 | 600 | 0.0650 | 6.02 | 7.78 | 0.228 | 3 | 0.07 | 1.89 | 0.058 | 3 | 87x |
| d35d29df0546 | 600 | 0.0595 | 6.10 | 7.82 | 0.227 | 2 | 0.09 | 1.81 | 0.047 | 1 | 65x |
| df617ef7fa25 | 600 | 0.0737 | 6.05 | 7.53 | 0.212 | 1 | 0.05 | 1.53 | 0.067 | 4 | 127x |

**Selections**

| selector | permutation | tree | same? |
|---|---|---|---|
| risk_only | 99c56a33fdd7 | 99c56a33fdd7 | yes |
| stable_5pct | 99c56a33fdd7 | 99c56a33fdd7 | yes |
| knee | d35d29df0546 | 99c56a33fdd7 | NO |

Stability ranking identical across explainers: False
