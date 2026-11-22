"""Build one Phase 1 candidate table from the saved 12-candidate run.

Joins three files from the run folder:
  candidate_pool.json         -> stream order and full configuration
  candidate_evaluations.csv   -> validation (inner-fold) risk and stability
  timings.csv                 -> fit time for the risk evaluation
Writes candidate_table.csv next to this script. Uses only the standard library.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "experiments/03_timing_pilot/results/elijah_12_candidates_20261119_104057_601869"

pool = json.loads((RUN / "breast_cancer/candidate_pool.json").read_text())
config = json.loads((RUN / "resolved_config.json").read_text())
evals = {r["candidate_id"]: r for r in csv.DictReader(
    open(RUN / "breast_cancer/outer_fold_0/candidate_evaluations.csv"))}
times = {r["candidate_id"]: r for r in csv.DictReader(open(RUN / "timings.csv"))
         if r["phase"] == "selection"}

# Seeds used for this fold, following benchmark.py and evaluation.py
fold_seed = config["base_seed"] + 0 * 100000          # outer fold 0
risk_split_seed = fold_seed + 4
model_seeds = [risk_split_seed + 1000 + k for k in range(config["inner_folds"])]

rows = []
for position, cand in enumerate(pool, start=1):
    cid = cand["candidate_id"]
    e, t = evals[cid], times[cid]
    rows.append({
        "stream_position": position,
        "candidate_id": cid,
        "family": cand["family"],
        "scaler": cand["preprocessing"]["scaler"],
        "imputer": cand["preprocessing"]["numeric_imputer"],
        "model_params": json.dumps(cand["model"], sort_keys=True),
        "pool_seed": config["candidate_pool"]["seed"],
        "inner_split_seed": risk_split_seed,
        "model_seeds": " ".join(map(str, model_seeds)),
        "validation_risk_mean": round(float(e["risk_mean"]), 5),
        "validation_risk_se": round(float(e["risk_se"]), 5),
        "fit_seconds_risk": round(float(t["risk_fit_seconds"]), 3),
        "fit_calls_risk": int(float(t["risk_fit_calls"])),
    })

out = HERE / "candidate_table.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} candidates to {out}")
