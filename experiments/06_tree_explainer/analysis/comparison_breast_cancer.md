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
