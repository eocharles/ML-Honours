import csv
import inspect
import runpy
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from functools import wraps

import explanation_stability.evaluation as ev

run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
output = Path("results") / ("elijah_12_alternating_" + run_id)
checkpoint = Path("checkpoints") / ("elijah_12_alternating_" + run_id)
output.mkdir(parents=True, exist_ok=False)

records = []
active = None
inside_stability = False


def measure(name, function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return function(*args, **kwargs)
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

original_vectors = ev._attribution_vectors


@wraps(original_vectors)
def timed_vectors(*args, **kwargs):
    global inside_stability
    previous = inside_stability
    inside_stability = True
    start = perf_counter()
    try:
        return original_vectors(*args, **kwargs)
    finally:
        if active is not None:
            active["stability_vectors_seconds"] += perf_counter() - start
        inside_stability = previous


ev._attribution_vectors = timed_vectors


def track_candidate(function, phase):
    signature = inspect.signature(function)

    @wraps(function)
    def wrapper(*args, **kwargs):
        global active
        candidate = signature.bind(*args, **kwargs).arguments["candidate"]
        row = {
            "phase": phase,
            "candidate_id": candidate["candidate_id"],
            "family": candidate["family"],
            "status": "running",
            "stability_vectors_seconds": 0.0,
        }
        for name in ("risk_fit", "stability_fit", "shap", "comparison"):
            row[name + "_seconds"] = 0.0
            row[name + "_calls"] = 0

        active = row
        start = perf_counter()
        print(f"Starting {phase}: {candidate['family']}", flush=True)
        try:
            result = function(*args, **kwargs)
            row["status"] = (
                result[0].status if phase == "selection" else "ok"
            )
            return result
        except BaseException:
            row["status"] = "interrupted_or_failed"
            raise
        finally:
            row["candidate_total_seconds"] = perf_counter() - start
            row["stability_total_seconds"] = (
                row["stability_vectors_seconds"] + row["comparison_seconds"]
            )
            records.append(row)
            active = None
            with (output / "timings.csv").open("w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=list(row))
                writer.writeheader()
                writer.writerows(records)
            print(
                f"  {row['status']} | "
                f"stability training: {row['stability_fit_seconds']:.2f}s | "
                f"SHAP: {row['shap_seconds']:.2f}s | "
                f"full stability check: {row['stability_total_seconds']:.2f}s",
                flush=True,
            )
    return wrapper


ev.evaluate_candidate = track_candidate(ev.evaluate_candidate, "selection")
ev.evaluate_selected_candidate = track_candidate(
    ev.evaluate_selected_candidate, "final"
)

sys.argv = [
    "experiments/run_benchmark.py",
    "--config", "configs/elijah_12_candidates.yaml",
    "--datasets", "configs/datasets.smoke.yaml",
    "--dataset-name", "breast_cancer",
    "--outer-fold", "0",
    "--output", str(output),
    "--checkpoints", str(checkpoint),
]

print("Results folder:", output, flush=True)

import explanation_stability.benchmark as benchmark

original_pool_generator = benchmark.generate_candidate_pool

def alternating_pool(*args, **kwargs):
    pool = original_pool_generator(*args, **kwargs)
    rf = [c for c in pool if c["family"] == "random_forest"]
    gb = [c for c in pool if c["family"] == "gradient_boosting"]
    assert len(rf) == len(gb) == 6
    ordered = [c for pair in zip(gb, rf) for c in pair]
    assert {c["candidate_id"] for c in ordered} == {
        c["candidate_id"] for c in pool
    }
    return ordered

benchmark.generate_candidate_pool = alternating_pool

runpy.run_path("experiments/run_benchmark.py", run_name="__main__")
print("\nFinished. Timing results:", output / "timings.csv", flush=True)
