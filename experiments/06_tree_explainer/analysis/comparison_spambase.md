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
