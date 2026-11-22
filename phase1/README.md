# Phase 1: Simple candidate-search baseline

Roadmap goal: define what is being optimized and what an AutoML candidate contains, and produce a reproducible candidate stream.
Status: complete, awaiting supervisor review.

| Roadmap requirement | Where it is |
|---|---|
| Dataset note | [DATASET.md](DATASET.md) |
| Strict train/development/test protocol, preprocessing inside folds, no test leakage | [PROTOCOL.md](PROTOCOL.md) |
| Declared search space | [PROTOCOL.md](PROTOCOL.md#search-space) |
| 12-20 row candidate table (config, seed, validation score, fit time) | [candidate_table.csv](candidate_table.csv), built by [make_candidate_table.py](make_candidate_table.py) |
| Fixed stream saved to disk | `experiments/03_timing_pilot/results/elijah_12_candidates_*/breast_cancer/candidate_pool.json` |
| Stream can be replayed | Smoke test rerun on Nov 21 gave identical `candidate_evaluations.csv` to Nov 19; grouped and alternating 12-candidate runs gave identical scores |
| Earlier baseline experiments | [01_smoke_test](../experiments/01_smoke_test), [02_tolerance](../experiments/02_tolerance) |

## What is optimized
Two objectives, both minimized:
1. **Predictive risk** (`risk_mean`): Brier score (squared probability loss) for classification, mean squared error for regression, averaged over inner folds.
2. **Explanation instability** (`magnitude_disagreement`): how much a candidate's mean absolute SHAP vector changes when it is refitted on different subsamples of the development data.

## What a candidate contains
A candidate is a recipe, not a fitted model: model family (Random Forest or Gradient Boosting), model hyperparameters, and preprocessing (numeric imputer and scaler). Each candidate gets an ID that is a hash of its full configuration, so the same recipe always has the same ID.
