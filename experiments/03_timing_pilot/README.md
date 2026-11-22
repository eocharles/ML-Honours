# Experiment 03: SHAP timing pilot (Phase 2)

## Purpose
I wanted to measure how long one complete explanation evaluation takes for each candidate, and which part of it (retraining, SHAP or comparison) costs the most. In this pilot, Random Forest candidates spent much more time on SHAP than Gradient Boosting candidates. Knowing where the cost comes from is the first step before deciding which candidates are worth spending a SHAP budget on.

## Important: units
All timing columns are in **seconds of compute time**. They are NOT SHAP values and NOT stability scores.
Explanation stability is measured separately by `magnitude_disagreement` in `candidate_evaluations.csv` (lower = more stable).

## Setup
- Code: Dania's explanation-stability-selection, commit `6bb5a1e`, run with `PYTHONPATH=src`
- Machine: my Windows laptop (Python 3.14.0, scikit-learn 1.9.1). Not Fir; my cluster request was pending.
- Dataset: breast_cancer (569 rows, 30 features), classification, outer fold 0
- Settings: 2 inner folds, 2 perturbations, 8 evaluation rows, 4 background rows, 2 SHAP permutations
- SHAP method: the repository's own permutation SHAP (`permutation_shap_values`), not the `shap` library's TreeExplainer
- Candidates come from `generate_candidate_pool()`, which uses its own built-in ranges (RF 200-600 trees, GB 100-400 trees), not the YAML `search_space` section. The actual recipes are saved in each run's `candidate_pool.json`.
- Scripts were written with help from ChatGPT; I ran the experiments and reran one myself on Nov 21.

## How to reproduce
From the `explanation-stability-selection` folder (Command Prompt):
```
.venv\Scripts\activate
set PYTHONPATH=src
python elijah_timing.py                  # 2-candidate smoke test
python elijah_timing_12.py               # 6 RF + 6 GB candidates
python elijah_timing_12_alternating.py   # same 12, alternating order
```
The scripts are in `scripts/` and the 12-candidate config in `configs/`. Each run creates a new timestamped results and checkpoints folder, so no cached work is reused.

## How the timing works
The scripts wrap Dania's functions like a coat: a stopwatch starts just before her function runs and stops when it finishes, and the time is added to that candidate's row. The wrapper passes the same inputs in and returns her function's output unchanged, so it only measures time. This is confirmed by my Nov 21 rerun, where `candidate_evaluations.csv` was identical to the Nov 19 run.

## What each column means
| Column | Meaning |
|---|---|
| risk_fit_seconds | Training for predictive risk (inner folds) |
| stability_fit_seconds | Retraining on each perturbed sample |
| shap_seconds | All SHAP calls for the candidate |
| comparison_seconds | Computing disagreement, rank and top-k agreement |
| stability_total_seconds | stability_vectors_seconds + comparison_seconds |
| candidate_total_seconds | The whole evaluation of one candidate |

The columns are nested (`shap_seconds` is already included in `stability_total_seconds`, which is included in `candidate_total_seconds`), so adding them together would count the same time more than once.

`selection` and `final` rows are different evaluation stages and must be analysed separately.

## Runs
| Folder | What it is |
|---|---|
| elijah_timing_20261119_* (3 runs) | 2-candidate smoke test, repeated |
| elijah_timing_20261121_205629_387713 | My own rerun of the smoke test |
| elijah_12_candidates_* | 6 RF + 6 GB candidates |
| elijah_12_alternating_* | Same 12 candidates, alternating GB/RF order |

## Results
Smoke test, selection stage, SHAP seconds:

| Run | RF | GB | Ratio |
|---|---|---|---|
| Nov 19 run 1 | 4.64 | 0.97 | 4.8x |
| Nov 19 run 2 | 4.57 | 0.25 | 18x |
| Nov 19 run 3 | 4.00 | 0.87 | 4.6x |
| Nov 21 (my rerun) | 4.11 | 1.02 | 4.0x |

12-candidate run: RF SHAP time grew with the number of trees (about 4.7 s at 200, 7.7 s at 400, 11 s at 600), while GB stayed around 0.85 s. Depth had little visible effect.

RF spent much more time on SHAP than GB, while retraining took about the same time for both in the smoke test. In the 12-candidate run, RF's SHAP time increased with the number of trees, and depth made little visible difference. GB's SHAP time stayed around 0.85 s, but its retraining time roughly doubled when its trees went from 200 to 400. One GB run had an unusually low SHAP time (0.25 s); I kept it, but it inflates that run's ratio to 18x, so a single run should not be trusted. Running the 12 candidates in a different order did not change the pattern, and my Nov 21 rerun gave identical `candidate_evaluations.csv`, so the results are reproducible.

The full write-up is in `Elijah_Charles_Timing_Pilot_Report.pdf`.

## Limitations
- One dataset and one outer fold: the pattern may differ on other data.
- Laptop, not the cluster: timings depend on hardware and background activity; comparable runs on Fir are still needed.
- Small settings (2 perturbations, 8 rows, 2 SHAP permutations): real runs use more, so absolute times will be larger.
- Few repeats: 4 smoke runs and only one run per order for the 12 candidates, and GB timings were noisy.
- Family vs settings: RF and GB had different tree counts, so the difference may come from the settings rather than the model family itself.
- The timing scripts have not had a dedicated test yet; call counts and identical outputs are only initial checks.

## Next steps
- Repeat the smoke and 12-candidate timing on Fir, recording cores and memory.
- Add a second classification dataset with about twice as many features as breast_cancer, recording rows, features and model settings.
- Test whether RF's SHAP cost follows the number of trees (for example 50, 100, 200, 400 and 600 trees, depth fixed, 3 repeats each).
