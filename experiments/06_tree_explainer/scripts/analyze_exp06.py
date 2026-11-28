"""Experiment 06 analysis: permutation SHAP vs TreeExplainer on the same random forests.

Usage: python analyze_exp06.py <results folder> <output folder>

For each dataset writes one short table (comparison_<dataset>.md and a combined
comparison.md) with, per RF candidate (selection stage):
  SHAP seconds, whole stability-check seconds, disagreement, and its stability rank,
  for both explainers, plus which candidate each selector picks.
Also writes tree_sweep.png / tree_sweep.csv (SHAP seconds vs number of trees).
Incomplete runs (riccardo permutation) are marked, never filled in.
"""
import csv, glob, json, statistics as st, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
EXPL = ["permutation", "tree"]
BLUE, ORANGE, INK, MUTED = "#257de0", "#f47230", "#1f1f1f", "#6b6b6b"

def rd(p): return list(csv.DictReader(open(p)))
def first(pattern):
    hits = sorted(glob.glob(str(pattern))); return Path(hits[0]) if hits else None

datasets = sorted({p.name for p in (ROOT / "rf_pool_tree").glob("*")})
sizes, combined, summary = {}, [], []
for ds in datasets:
    data = {}
    for ex in EXPL:
        runs = sorted((ROOT / f"rf_pool_{ex}" / ds).glob("rep*"))
        timing, evals, picks, complete = {}, {}, {}, False
        for run in runs:
            for r in rd(run / "timings.csv"):
                if r["phase"] == "selection":
                    timing.setdefault(r["candidate_id"], {"trees": int(r["n_estimators"]), "shap": [], "stab": []})
                    timing[r["candidate_id"]]["shap"].append(float(r["shap_seconds"]))
                    timing[r["candidate_id"]]["stab"].append(float(r["stability_total_seconds"]))
            meta = first(run / "*" / "dataset.json")
            if meta: m = json.loads(meta.read_text()); sizes[ds] = (m.get("n_rows"), m.get("n_features"))
        if runs:
            final = first(runs[0] / "*/outer_fold_0/candidate_evaluations.csv")
            partial = first(runs[0] / "*/outer_fold_0/candidate_evaluations.partial.csv")
            complete = final is not None
            src = final or partial
            if src: evals = {r["candidate_id"]: r for r in rd(src)}
            sel = first(runs[0] / "*/outer_fold_0/selections.json")
            if sel: picks = {s["selector"]: s["candidate_id"] for s in json.loads(sel.read_text())}
        data[ex] = {"timing": timing, "evals": evals, "picks": picks, "complete": complete, "repeats": len(runs)}
        # stability rank among candidates that finished (1 = most stable)
        done = sorted(evals, key=lambda c: float(evals[c]["magnitude_disagreement"]))
        data[ex]["rank"] = {c: i + 1 for i, c in enumerate(done)}

    order = sorted(data["tree"]["timing"], key=lambda c: (data["tree"]["timing"][c]["trees"], c))
    rows = []
    for c in order:
        row = {"candidate": c, "trees": data["tree"]["timing"][c]["trees"],
               "risk (Brier)": f"{float(data['tree']['evals'][c]['risk_mean']):.4f}" if c in data["tree"]["evals"] else "-"}
        for ex in EXPL:
            t, e = data[ex]["timing"].get(c), data[ex]["evals"].get(c)
            row[f"SHAP s ({ex})"] = f"{st.median(t['shap']):.2f}" if t else "not run"
            row[f"stability s ({ex})"] = f"{st.median(t['stab']):.2f}" if t else "not run"
            row[f"disagreement ({ex})"] = f"{float(e['magnitude_disagreement']):.3f}" if e else "not run"
            row[f"rank ({ex})"] = data[ex]["rank"].get(c, "-") if data[ex]["complete"] else "-"
        p, tr = data["permutation"]["timing"].get(c), data["tree"]["timing"].get(c)
        row["SHAP speed-up"] = f"{st.median(p['shap']) / st.median(tr['shap']):.0f}x" if p and tr else "-"
        rows.append(row); combined.append({"dataset": ds, **row})

    n, f = sizes.get(ds, ("?", "?"))
    lines = [f"### {ds} ({n} rows, {f} features)\n"]
    for ex in EXPL:
        d = data[ex]; state = "complete" if d["complete"] else f"INCOMPLETE ({len(d['evals'])} of {len(order)} candidates finished)"
        lines.append(f"- {ex}: {d['repeats']} repeat(s), {state}")
    lines.append("\n| " + " | ".join(rows[0]) + " |\n|" + "---|" * len(rows[0]))
    lines += ["| " + " | ".join(str(v) for v in r.values()) + " |" for r in rows]
    lines.append("\n**Selections**\n\n| selector | permutation | tree | same? |\n|---|---|---|---|")
    for s in ("risk_only", "stable_5pct", "knee"):
        a, b = data["permutation"]["picks"].get(s, "not finished"), data["tree"]["picks"].get(s, "not finished")
        lines.append(f"| {s} | {a} | {b} | {'yes' if a == b else ('-' if 'not' in a + b else 'NO')} |")
    common = [c for c in order if c in data["permutation"]["rank"] and c in data["tree"]["rank"]]
    same_rank = all(data["permutation"]["rank"][c] == data["tree"]["rank"][c] for c in common) if data["permutation"]["complete"] else None
    lines.append(f"\nStability ranking identical across explainers: {same_rank if same_rank is not None else 'cannot tell yet (permutation incomplete)'}\n")
    text = "\n".join(lines)
    (OUT / f"comparison_{ds}.md").write_text(text)
    summary.append(text)

(OUT / "comparison.md").write_text("All times are seconds of compute time (selection stage, median over repeats). "
    "Disagreement: lower = more stable; rank 1 = most stable. Same seeds, so the forests are identical for both explainers.\n\n"
    + "\n\n".join(summary))
with open(OUT / "comparison.csv", "w", newline="") as fh:
    keys = list(combined[0]); w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(combined)

# ---- tree sweep: SHAP seconds vs trees, both explainers ----
pts = []
for ex in EXPL:
    for ds_dir in sorted((ROOT / f"tree_sweep_{ex}").glob("*")):
        by = {}
        for run in ds_dir.glob("rep*"):
            for r in rd(run / "timings.csv"):
                if r["phase"] == "selection":
                    by.setdefault(int(r["n_estimators"]), []).append(float(r["shap_seconds"]))
        for t, v in sorted(by.items()):
            pts.append({"dataset": ds_dir.name, "explainer": ex, "n_estimators": t, "repeats": len(v),
                        "shap_median_s": round(st.median(v), 4), "shap_min_s": round(min(v), 4), "shap_max_s": round(max(v), 4)})
with open(OUT / "tree_sweep.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(pts[0])); w.writeheader(); w.writerows(pts)
sweep_ds = sorted([d for d in datasets if any(p["dataset"] == d for p in pts)], key=lambda d: (sizes.get(d, (0, 0))[1] or 0))
from matplotlib.ticker import FuncFormatter
fig, axes = plt.subplots(1, len(sweep_ds), figsize=(5.2 * len(sweep_ds), 4.4), squeeze=False, sharey=True)
for ax, ds in zip(axes[0], sweep_ds):
    for ex, color, label in (("permutation", BLUE, "Permutation SHAP"), ("tree", ORANGE, "TreeExplainer")):
        p = [q for q in pts if q["dataset"] == ds and q["explainer"] == ex]
        if not p: continue
        x = [q["n_estimators"] for q in p]; y = [q["shap_median_s"] for q in p]
        ax.errorbar(x, y, yerr=[[q["shap_median_s"] - q["shap_min_s"] for q in p], [q["shap_max_s"] - q["shap_median_s"] for q in p]],
                    color=color, lw=2, marker="o", ms=5, capsize=3, label=label)
    n, f = sizes.get(ds, ("?", "?"))
    ax.set_title(f"{ds} ({n} rows, {f} features)", fontsize=10, color=INK)
    ax.set_yscale("log"); ax.set_xlabel("Number of trees (Random Forest)", color=INK)
    if ax is axes[0][0]: ax.set_ylabel("SHAP time per candidate (seconds, log scale)", color=INK)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.grid(axis="y", which="both", color="#eeeeee"); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5)
fig.suptitle("SHAP time vs number of trees: permutation SHAP vs TreeExplainer (same forests)", fontsize=11, color=INK)
fig.text(0.01, 0.01, "RF depth 8, sqrt features; 2 refits, 8 explained rows, 4 background rows; permutation uses 2 permutations. "
         "Points: median of repeats, bars: min-max.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 0.95)); fig.savefig(OUT / "tree_sweep.png", dpi=200); plt.close(fig)
print("Wrote:", ", ".join(sorted(p.name for p in OUT.iterdir())))
