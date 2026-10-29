\# Experiment 02: Selection Threshold (Tolerance)



\*\*Date:\*\* October 29, 2026

\*\*Config:\*\* `elijah\_tolerance.yaml` (a copy of smoke.yaml with `relative\_tolerances: \[0.05, 0.10, 0.20, 0.25]`)

\*\*Runs:\*\* breast\_cancer and diabetes, outer folds 0 and 1 (laptop)



In my first runs, all three selectors always picked the model with the lowest risk, so stability never decided anything. My hypothesis was that the 5% threshold was the reason: the other model was never within 5% of the best risk, so the stability rule had only one candidate to choose from. I loosened the threshold to 10%, 20% and 25% and predicted in advance where each run would switch to the more stable model. All 16 selections matched my predictions, so the selectors only consider stability once the other model is close enough in accuracy. The cost of choosing stability varied a lot: on breast\_cancer I gave up about 5.5% accuracy for explanations about 4 times more stable, but on diabetes I gave up 13.5% to 22% accuracy for only 12% to 18% better stability.



Full write-up: `../Self\_Directed\_Experiments\_A\_B\_Elijah\_Charles.docx`

