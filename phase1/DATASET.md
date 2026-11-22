# Dataset note: breast_cancer

| Property | Value |
|---|---|
| Name | Breast Cancer Wisconsin (Diagnostic) |
| Source | scikit-learn built-in copy (`sklearn.datasets.load_breast_cancer`); original from the UCI Machine Learning Repository |
| Task | Binary classification (malignant vs benign) |
| Rows | 569 |
| Features | 30, all numeric (measurements of cell nuclei from images, such as radius, texture and area) |
| Classes | 212 malignant, 357 benign |
| Missing values | None |

## Why this dataset
- Small, public and already used in the supervisors' smoke configuration, so results can be checked against theirs.
- Fast enough to run many repeats on a laptop and on the cluster.
- All numeric features, so preprocessing differences between candidates stay simple.
- 30 features gives a baseline for the Phase 2 question of how SHAP cost grows with the number of features.

Regression results (diabetes) from the earlier experiments are kept separate and are not used for the classification comparisons.
