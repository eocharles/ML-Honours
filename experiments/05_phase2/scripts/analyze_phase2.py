"""Make the Phase 2 table and plots from the raw results.

Usage:  python analyze_phase2.py <results/phase2 folder> <output folder>

Reads every run's timings.csv, candidate_evaluations.csv, selections.json and
dataset.json. Writes:
  dataset_sizes.csv              rows / features per dataset
  timing_breakdown.csv / .md     median and range of each timing part (deliverable 1)
  reproducibility.csv            whether scores were identical across repeats
  tree_sweep.csv, tree_sweep.png SHAP seconds vs number of trees (deliverable 2)
  selection_cost.csv, selection_cost.png
                                 Brier loss vs disagreement with stability cost (deliverable 3)
All times are seconds of compute time.
"""
import csv, json, statistics as st, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, INK, MUTED = "#257de0", "#f47230", "#1f1f1f", "#6b6b6b"
FAMILY_COLOR = {"random_forest": BLUE, "gradient_boosting": ORANGE}
DATASET_COLOR = {}  # filled in order of appearance

def runs(experiment):
    for ds_dir in sorted((ROOT / experiment).glob("*")):
        for run in sorted(ds_dir.glob("rep*")):
            yield ds_dir.name, run

def read_csv(p): return list(csv.DictReader(open(p)))
def write_csv(p, rows):
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def fmt(values): return f"{st.median(values):.3f} [{min(values):.3f}-{max(values):.3f}]"

# ---- dataset sizes ----
sizes = {}
for exp in ("pool12", "tree_sweep"):
    for ds, run in runs(exp):
        meta = json.loads(next(run.glob("*/dataset.json")).read_text())
        sizes[ds] = {"dataset": ds, "rows": meta.get("n_rows"), "features": meta.get("n_features")}
write_csv(OUT / "dataset_sizes.csv", list(sizes.values()))
for i, ds in enumerate(sizes): DATASET_COLOR[ds] = [BLUE, ORANGE][i % 2]

# ---- deliverable 1: timing breakdown (pool12) ----
parts = ["risk_fit_seconds", "stability_fit_seconds", "shap_seconds",
         "comparison_seconds", "stability_total_seconds", "candidate_total_seconds"]
groups = {}
for ds, run in runs("pool12"):
    for r in read_csv(run / "timings.csv"):
        groups.setdefault((ds, r["phase"], r["family"]), []).append(r)
table = []
for (ds, phase, fam), rows in sorted(groups.items(), key=lambda k: (k[0][0], k[0][1] != "selection", k[0][2])):
    row = {"dataset": ds, "phase": phase, "family": fam, "n_measurements": len(rows)}
    for p in parts:
        row[p.replace("_seconds", "") + " (median [min-max] s)"] = fmt([float(r[p]) for r in rows])
    table.append(row)
write_csv(OUT / "timing_breakdown.csv", table)
with open(OUT / "timing_breakdown.md", "w") as f:
    f.write("All values are seconds: median [min-max] over every candidate and repeat in the group.\n"
            "stability_total = stability refits + SHAP + comparison (plus small overhead). Columns are nested; do not add them.\n\n")
    f.write("| " + " | ".join(table[0]) + " |\n|" + "---|" * len(table[0]) + "\n")
    for row in table: f.write("| " + " | ".join(str(v) for v in row.values()) + " |\n")

# ---- reproducibility across repeats ----
repro = []
for exp in ("pool12", "tree_sweep"):
    seen = {}
    for ds, run in runs(exp):
        text = next(run.glob("*/outer_fold_0/candidate_evaluations.csv")).read_text()
        seen.setdefault(ds, set()).add(text)
    for ds, texts in seen.items():
        repro.append({"experiment": exp, "dataset": ds, "identical_scores_across_repeats": len(texts) == 1})
write_csv(OUT / "reproducibility.csv", repro)

# ---- deliverable 2: tree sweep ----
sweep, by = [], {}
for ds, run in runs("tree_sweep"):
    for r in read_csv(run / "timings.csv"):
        if r["phase"] == "selection":
            by.setdefault((ds, int(r["n_estimators"])), []).append(float(r["shap_seconds"]))
for (ds, trees), v in sorted(by.items()):
    sweep.append({"dataset": ds, "n_estimators": trees, "repeats": len(v), "shap_median_s": round(st.median(v), 3),
                  "shap_min_s": round(min(v), 3), "shap_max_s": round(max(v), 3)})
if sweep:
    write_csv(OUT / "tree_sweep.csv", sweep)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for ds in sizes:
        pts = [s for s in sweep if s["dataset"] == ds]
        if not pts: continue
        x = [p["n_estimators"] for p in pts]; y = [p["shap_median_s"] for p in pts]
        lo = [p["shap_median_s"] - p["shap_min_s"] for p in pts]; hi = [p["shap_max_s"] - p["shap_median_s"] for p in pts]
        label = f"{ds} ({sizes[ds]['rows']} rows, {sizes[ds]['features']} features)"
        ax.errorbar(x, y, yerr=[lo, hi], color=DATASET_COLOR[ds], lw=2, marker="o", ms=6, capsize=3, label=label)
    ax.set_xlabel("Number of trees (Random Forest)", color=INK)
    ax.set_ylabel("SHAP time per candidate (seconds)", color=INK)
    ax.set_title("SHAP time vs number of trees\nRF depth 8, sqrt features, 2 perturbations x 2 SHAP permutations, 8 rows, 1 core",
                 fontsize=10, color=INK)
    ax.set_ylim(bottom=0); ax.grid(axis="y", color="#e6e6e6"); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.text(0.01, 0.01, "Points: median of repeats; bars: min-max.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "tree_sweep.png", dpi=200); plt.close(fig)

# ---- deliverable 3: selection vs cost (pool12) ----
sel_rows, datasets = [], sorted({ds for ds, _ in runs("pool12")})
if datasets:
    fig, axes = plt.subplots(1, len(datasets), figsize=(6.5 * len(datasets), 5), squeeze=False)
    for ax, ds in zip(axes[0], datasets):
        ds_runs = [run for d, run in runs("pool12") if d == ds]
        ev = {r["candidate_id"]: r for r in read_csv(next(ds_runs[0].glob("*/outer_fold_0/candidate_evaluations.csv")))}
        picks = {s["selector"]: s["candidate_id"] for s in json.loads(next(ds_runs[0].glob("*/outer_fold_0/selections.json")).read_text())}
        cost = {}
        for run in ds_runs:
            for r in read_csv(run / "timings.csv"):
                if r["phase"] == "selection":
                    cost.setdefault(r["candidate_id"], []).append(float(r["stability_total_seconds"]))
        max_cost = max(st.median(v) for v in cost.values())
        for cid, e in ev.items():
            c = st.median(cost[cid]); x, y = float(e["risk_mean"]), float(e["magnitude_disagreement"])
            sel_rows.append({"dataset": ds, "candidate_id": cid, "family": e["family"], "validation_brier": round(x, 5),
                             "disagreement": round(y, 5), "stability_cost_median_s": round(c, 3),
                             "risk_only_pick": cid == picks.get("risk_only"), "stable_5pct_pick": cid == picks.get("stable_5pct")})
            ax.scatter(x, y, s=40 + 360 * c / max_cost, color=FAMILY_COLOR.get(e["family"], MUTED), alpha=0.85,
                       edgecolor="white", linewidth=1.5, zorder=3)
            ax.annotate(f"{c:.1f}s", (x, y), xytext=(9, 4), textcoords="offset points", fontsize=7.5, color=MUTED,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85), zorder=5)
        same = picks.get("risk_only") == picks.get("stable_5pct")
        labels = ((("risk_only", "risk_only and stable_5pct pick", (-5, -95)),) if same else
                  (("risk_only", "risk_only pick", (-10, 45)), ("stable_5pct", "stable_5pct pick", (40, -26))))
        for selector, marker_label, off in labels:
            cid = picks.get(selector)
            if cid in ev:
                x, y = float(ev[cid]["risk_mean"]), float(ev[cid]["magnitude_disagreement"])
                ax.scatter(x, y, s=420, facecolor="none", edgecolor=INK, linewidth=1.5, zorder=4)
                ax.annotate(marker_label, (x, y), xytext=off, textcoords="offset points", fontsize=8.5, color=INK,
                            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
                            arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
        ax.set_title(f"{ds} ({sizes[ds]['rows']} rows, {sizes[ds]['features']} features)"
                     + ("\nboth rules pick the same candidate" if same else "\nthe two rules pick different candidates"),
                     fontsize=10, color=INK)
        ax.set_xlabel("Validation Brier loss (lower is better)", color=INK)
        ax.set_ylabel("SHAP disagreement (lower is more stable)", color=INK)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
        ax.grid(color="#eeeeee"); ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Line2D([], [], marker="o", ls="", color=FAMILY_COLOR[f], ms=8, label=f.replace("_", " ").title())
               for f in FAMILY_COLOR]
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=9)
    fig.text(0.01, 0.01, "Marker size and label: median seconds for the full stability check (refits + SHAP + comparison).",
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 0.93, 1)); fig.savefig(OUT / "selection_cost.png", dpi=200); plt.close(fig)
    write_csv(OUT / "selection_cost.csv", sel_rows)

print("Wrote:", ", ".join(sorted(p.name for p in OUT.iterdir())))
