\# Experiment 01: Smoke Test



\*\*Date:\*\* October 22, 2026

\*\*Dataset:\*\* breast\_cancer

\*\*Outer fold:\*\* 0

\*\*Models:\*\* Random Forest, Gradient Boosting (one configuration each)

\*\*Code:\*\* Dania's explanation-stability-selection repository (version 0.6.0rc2)



\## Setup



Siku rejected my login after Duo (access not enabled yet), so I ran the smoke test locally on my laptop (Windows, Python 3.14.0).



Command used:



&#x20;   python experiments/run\_benchmark.py --config configs/smoke.yaml --datasets configs/datasets.smoke.yaml --dataset-name breast\_cancer --outer-fold 0 --output results/elijah\_pilot --checkpoints checkpoints/elijah\_pilot



The results are in the `results/` folder.



\## Results



| Model | risk\_mean | risk\_se | magnitude\_disagreement | rank\_agreement | top\_k\_agreement |

|---|---|---|---|---|---|

| Random Forest | 0.0468 | 0.0035 | 0.1091 | 0.9595 | 1.0 |

| Gradient Boosting | 0.0444 | 0.0057 | 0.4682 | 0.6774 | 0.5 |



Selected model (all three selectors: risk\_only, stable\_5pct, knee): \*\*Gradient Boosting\*\*



\## Answers



\*\*1. Which model has the lowest predictive error?\*\*

Gradient Boosting has the lowest predictive error (risk\_mean) of 0.0444, while Random Forest has 0.0468. Lower is better. However, they only differ by about 0.0024, which is smaller than the standard error (risk\_se) of both models (0.0035 for RF and 0.0057 for GB). So GB is ahead, but not by a clearly meaningful amount.



\*\*2. Which model has the most stable explanations?\*\*

Random Forest. magnitude\_disagreement measures how much the explanations change when the model is retrained. RF is 0.1091 and GB is 0.4682, so GB's explanations change about 4 times as much. The other stability measures agree: RF has higher rank\_agreement (0.96 vs 0.68) and top\_k\_agreement (1.0 vs 0.5).



\*\*3. Does selecting based on prediction alone give the same model as considering explanation stability?\*\*

Yes. All three selectors (risk\_only, stable\_5pct and knee) chose Gradient Boosting. But this happened because Random Forest's risk\_mean (0.046845) was just above the stable\_5pct threshold (0.046645, which is 5% above the best risk), so only GB was eligible and the stability-aware rule never got to compare stability. The result depended on the threshold, and with only 2 candidates there was not much for the selectors to choose between.



\## Open questions



\- What exactly does "risk" measure (error rate or another loss)?

\- What do raw\_mean\_standard\_deviation and mean\_total\_attribution measure?

\- How does the knee selector work?

\- Should my ML-Honours repo be public or private?


## Re-run on Fir (October 29, 2026)

Ran the same command on the Fir cluster (compute node, Python 3.12, scikit-learn 1.8.0). Results are in `fir_results/`.

| | Laptop | Fir |
|---|---|---|
| RF risk_mean | 0.046845 | 0.046845 |
| RF magnitude_disagreement | 0.109106 | 0.109106 |
| GB risk_mean | 0.044424 | 0.044201 |
| GB magnitude_disagreement | 0.468174 | 0.459479 |

Random Forest results were identical, but Gradient Boosting changed slightly. My hypothesis is the different scikit-learn version (1.9.1 on my laptop vs 1.8.0 on Fir). The conclusions stayed the same: all three selectors still chose GB, and RF still fell just outside the 5% threshold (0.046845 vs 0.046411).

Lesson: record exact package versions with every experiment.
