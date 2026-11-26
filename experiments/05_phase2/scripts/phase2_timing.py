"""Phase 2 timing run: one repeat, one dataset.

Wraps the supervisors' functions with stopwatches (same method as experiment 03),
then runs their benchmark on outer fold 0. Results are unchanged; only time is measured.

Two modes:
  default       the fixed 12-candidate pool (6 RF + 6 GB) from the config
  --tree-sweep  Random Forest only, varying n_estimators, everything else fixed
"""
import argparse
import csv
from datetime import datetime
from functools import wraps
import inspect
from pathlib import Path
from time import perf_counter

import explanation_stability.evaluation as ev
import explanation_stability.candidates as cand
from explanation_stability.io import load_yaml

TREE_COUNTS = [25, 50, 100, 200, 400, 600, 800]
FIXED_RF = {"max_depth": 8, "min_samples_leaf": 1, "max_features": "sqrt"}
FIXED_PREP = {"scaler": "standard", "numeric_imputer": "median"}

p = argparse.ArgumentParser()
p.add_argument("--config", required=True)
p.add_argument("--datasets", required=True)
p.add_argument("--dataset-name", required=True)
p.add_argument("--data-root", required=True)
p.add_argument("--out-root", required=True)
p.add_argument("--repeat", type=int, required=True)
p.add_argument("--tree-sweep", action="store_true")
args = p.parse_args()

label = "tree_sweep" if args.tree_sweep else "pool12"
stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
output = Path(args.out_root) / label / args.dataset_name / f"rep{args.repeat}_{stamp}"
checkpoint = Path("checkpoints") / "phase2" / label / args.dataset_name / f"rep{args.repeat}_{stamp}"
output.mkdir(parents=True, exist_ok=False)

# ---- stopwatches (same logic as elijah_timing.py) ----
records, active, inside_stability = [], None, False

def measure(name, function):
    @wraps(function)
    def wrapper(*a, **k):
        start = perf_counter()
        try:
            return function(*a, **k)
        finally:
            if active is not None:
                key = name
                if name == "fit":
                    key = "stability_fit" if inside_stability else "risk_fit"
                active[key + "_seconds"] += perf_counter() - start
                active[key + "_calls"] += 1
    return wrapper

ev._fit_with_warning_capture = measure("fit", ev._fit_with_warning_capture)
ev.permutation_shap_values = measure("shap", ev.permutation_shap_values)
ev.summarize_stability = measure("comparison", ev.summarize_stability)
_original_vectors = ev._attribution_vectors

@wraps(_original_vectors)
def timed_vectors(*a, **k):
    global inside_stability
    previous, inside_stability = inside_stability, True
    start = perf_counter()
    try:
        return _original_vectors(*a, **k)
    finally:
        if active is not None:
            active["stability_vectors_seconds"] += perf_counter() - start
        inside_stability = previous

ev._attribution_vectors = timed_vectors

def track(function, phase):
    signature = inspect.signature(function)
    @wraps(function)
    def wrapper(*a, **k):
        global active
        c = signature.bind(*a, **k).arguments["candidate"]
        row = {"dataset": args.dataset_name, "experiment": label, "repeat": args.repeat,
               "phase": phase, "candidate_id": c["candidate_id"], "family": c["family"],
               "n_estimators": c["model"].get("n_estimators"), "max_depth": c["model"].get("max_depth"),
               "status": "running", "stability_vectors_seconds": 0.0}
        for n in ("risk_fit", "stability_fit", "shap", "comparison"):
            row[n + "_seconds"] = 0.0
            row[n + "_calls"] = 0
        active = row
        start = perf_counter()
        try:
            result = function(*a, **k)
            row["status"] = result[0].status if phase == "selection" else "ok"
            return result
        except BaseException:
            row["status"] = "interrupted_or_failed"
            raise
        finally:
            row["candidate_total_seconds"] = perf_counter() - start
            row["stability_total_seconds"] = row["stability_vectors_seconds"] + row["comparison_seconds"]
            records.append(row)
            active = None
            with (output / "timings.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(row))
                w.writeheader()
                w.writerows(records)
            print(f"  {phase:9s} {c['family']:17s} trees={row['n_estimators']} "
                  f"SHAP={row['shap_seconds']:.2f}s stability={row['stability_total_seconds']:.2f}s", flush=True)
    return wrapper

ev.evaluate_candidate = track(ev.evaluate_candidate, "selection")
ev.evaluate_selected_candidate = track(ev.evaluate_selected_candidate, "final")

# ---- tree sweep: replace the random pool with a fixed list ----
if args.tree_sweep:
    def tree_sweep_pool(**_ignored):
        pool = []
        for trees in TREE_COUNTS:
            c = {"family": "random_forest", "preprocessing": dict(FIXED_PREP),
                 "model": {"n_estimators": trees, **FIXED_RF}}
            c["candidate_id"] = cand._candidate_id(c)
            pool.append(c)
        return pool
    cand.generate_candidate_pool = tree_sweep_pool

# Import the benchmark only AFTER patching, so it picks up the wrapped functions.
from explanation_stability.benchmark import run_benchmark

config = load_yaml(args.config)
config["experiment_name"] = f"phase2_{label}"
print(f"{label} | {args.dataset_name} | repeat {args.repeat} -> {output}", flush=True)
run_benchmark(config, load_yaml(args.datasets)["datasets"], output,
              checkpoint_root=checkpoint, data_root=args.data_root,
              dataset_name=args.dataset_name, outer_fold=0)
print("done", flush=True)
