"""Sanity check: do TreeExplainer and permutation SHAP measure the same thing?

Fits one Random Forest pipeline (supervisors' build_pipeline) on breast_cancer, then:
  1. Additivity: TreeExplainer values per row should sum to
     f(row) - mean f(background rows).
  2. Convergence: permutation SHAP with many permutations should approach the
     exact TreeExplainer values (with 2 permutations it is a rough estimate).
"""
import time
import numpy as np
import shap
from sklearn.datasets import load_breast_cancer
from explanation_stability.models import build_pipeline, predict_for_attribution
from explanation_stability.attribution import permutation_shap_values

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
train, eval_rows, bg_rows = idx[:400], idx[400:408], idx[408:412]
candidate = {"family": "random_forest",
             "preprocessing": {"scaler": "standard", "numeric_imputer": "median"},
             "model": {"n_estimators": 200, "max_depth": 8, "min_samples_leaf": 1, "max_features": "sqrt"}}
pipe = build_pipeline(X, "classification", candidate, random_state=1)
pipe.fit(X.iloc[train], y.iloc[train])
Xe, Xb = X.iloc[eval_rows], X.iloc[bg_rows]
f = lambda frame: predict_for_attribution(pipe, frame, "classification")

pre, model = pipe.named_steps["preprocessor"], pipe.named_steps["model"]
t = time.perf_counter()
expl = shap.TreeExplainer(model, data=pre.transform(Xb), feature_perturbation="interventional",
                          model_output="probability")
tree = np.asarray(expl.shap_values(pre.transform(Xe), check_additivity=False))
tree = tree[:, :, 1] if tree.ndim == 3 else tree
t_tree = time.perf_counter() - t

expected = f(Xe) - f(Xb).mean()
print(f"1. Additivity: max |sum(SHAP) - (f(x) - mean f(background))| = {np.abs(tree.sum(1) - expected).max():.2e}")

print("2. Convergence (mean absolute difference from TreeExplainer, and seconds):")
print(f"   TreeExplainer: {t_tree:.3f} s")
for k in (2, 10, 50, 150):
    t = time.perf_counter()
    perm = permutation_shap_values(f, Xe, Xb, permutations=k, seed=7)
    print(f"   permutation x{k:<3}: diff = {np.abs(perm - tree).mean():.5f}   time = {time.perf_counter() - t:.2f} s")
print(f"   (typical |SHAP value| for scale: {np.abs(tree).mean():.5f})")
