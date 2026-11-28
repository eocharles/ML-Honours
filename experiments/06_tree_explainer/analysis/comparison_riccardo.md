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
