# ML-Honours

**Budgeted Optimization of Explanation Computation in AutoML**
Elijah Charles, Computer Science Honours, University of Prince Edward Island (2026-2027)
Supervisors: Dr. Dania Tamayo-Vera and Dr. Antonio Bolufe-Rohler

## Research question
AutoML searches through many candidate models. Choosing models that are both accurate and have stable SHAP explanations requires evaluating explanation stability, which is expensive. This project studies how to allocate a limited explanation budget during model search: which candidates are worth explaining, and how much decision quality is lost compared with explaining every candidate.

The experiments reuse the model, SHAP, stability and selection code from the supervisors' repository, [explanation-stability-selection](https://gitlab.com/university-of-prince-edward-isalnd/explanation-stability-selection).

## Progress by roadmap phase

| Phase | Goal | Status | Evidence |
|---|---|---|---|
| 1 | Simple candidate-search baseline: define what is optimized and what a candidate contains; reproducible candidate stream | Complete, needs supervisor review | [`phase1/`](phase1) (dataset note, protocol, candidate table), `experiments/01_smoke_test`, `experiments/02_tolerance`, candidate pool and reproducibility check in `experiments/03_timing_pilot` |
| 2 | Define one complete explanation evaluation and measure its real cost | In progress | `experiments/03_timing_pilot` |
| 3-7 | Allocation strategies, full audit, stress tests, thesis | Not started | |

### Phase 1 evidence
- **[phase1](phase1)**: dataset note, evaluation protocol, declared search space and the 12-candidate table.
- **[01_smoke_test](experiments/01_smoke_test)**: first runs of the benchmark (breast_cancer, diabetes; RF vs GB), including a laptop vs Fir comparison. Report: `Experiment01_Smoke_Test_Elijah_Charles.docx`.
- **[02_tolerance](experiments/02_tolerance)**: how the selection tolerance (5%, 10%, 20%, 25%) decides when explanation stability changes the selected model.
- **[Self_Directed_Experiments_A_B](experiments/Self_Directed_Experiments_A_B_Elijah_Charles.docx)**: write-up of the two experiments above.
- **Candidate stream**: the 12-candidate pool (6 RF, 6 GB) with configurations, risk and stability is saved in `experiments/03_timing_pilot/results/elijah_12_candidates_*`. Rerunning with the same seeds gave identical `candidate_evaluations.csv` (Nov 19 vs Nov 21).

### Phase 2 evidence
- **[03_timing_pilot](experiments/03_timing_pilot)**: timing of each part of an explanation evaluation (retraining, SHAP, comparison) for RF and GB on breast_cancer. Includes scripts, config, results, report and a README explaining every column.

## Notes
- All timing values are in **seconds of compute time**, not SHAP values. Stability is measured by `magnitude_disagreement` (lower is more stable).
- Classification and regression results are kept separate.
- Pilot runs so far were on a laptop; cluster (Fir) runs are next.
