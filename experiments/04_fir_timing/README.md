# Experiment 04: SHAP timing on Fir (Phase 2)

The same timing scripts as [03_timing_pilot](../03_timing_pilot), run on the Fir cluster with fixed resources so timings are comparable.

## Setup
- Job: `sbatch` script [`fir_timing_job.sh`](../03_timing_pilot/scripts/fir_timing_job.sh), job 5034257, Nov 21 2026
- Node fc30556, AMD EPYC 9655 96-Core Processor, **1 core**, 8 GB memory
- Python 3.12.4, scikit-learn 1.8.0, numpy 2.5.3; code commit `6bb5a1e`
- Dataset breast_cancer (569 rows, 30 features), outer fold 0, same smoke settings as experiment 03
- Runs: 3 smoke repeats, 12 candidates grouped, 12 candidates alternating. Full output in `timing_bc_5034257.log`.

All times are **seconds of compute time**, not SHAP values.

## Results
Smoke test, selection stage, SHAP seconds:

| Machine | RF runs | GB runs | RF/GB (median) |
|---|---|---|---|
| Laptop (4 runs) | 4.64, 4.57, 4.00, 4.11 | 0.97, 0.25, 0.87, 1.02 | 4.7x |
| Fir (3 runs) | 1.24, 1.22, 1.13 | 0.21, 0.20, 0.20 | 6.0x |

- Fir was about 3.5-4x faster than the laptop, and its timings were much more consistent (no outliers).
- RF SHAP time still grew with the number of trees (about 1.2 s at 200, 2.1 s at 400 and 3.0 s at 600 trees), while GB stayed around 0.2 s.
- RF/GB ratios were similar on both machines (about 6x for 200-tree RF, about 14x for 600-tree RF), so the relative cost looks like a property of the models rather than the machine.

## Reproducibility across machines
- All 6 Random Forest candidates had **identical** risk and disagreement scores on Fir and the laptop.
- The 6 Gradient Boosting candidates differed slightly (for example risk 0.04675 vs 0.04681). The likely cause is the different scikit-learn version (1.8.0 on Fir, 1.9.1 on the laptop), the same pattern seen in experiment 01.
- The selected models were identical on both machines: risk_only chose 99c56a33fdd7 (RF2), stable_5pct and knee chose df617ef7fa25 (RF4).

## Limitations
- One dataset, one fold, small smoke settings.
- Only 3 smoke repeats and one run per order for the 12 candidates.
- Laptop and Fir used different scikit-learn versions, so timings and GB scores are not directly comparable across machines; within-machine comparisons are the valid ones.
