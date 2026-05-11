#!/usr/bin/env python3
"""
analyze_exp2.py  —  Experiment 2 analysis
Compares WLM-SL / WLM-JSON / Baseline A / Baseline B
across 30 domain-independent tasks (T08-T37).

Usage:
    python analyze_exp2.py --tag exp2
    python analyze_exp2.py --tag exp2 --compare-exp1 full_v6
"""

import argparse, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from config import RESULTS_DIR, FIGURES_DIR

# ── Helpers ───────────────────────────────────────────────────────────────────

LARGE_MODELS  = ["claude", "gpt-4o"]
SMALL_MODELS  = ["gpt-4o-mini", "qwen-7b", "gemma-4b"]
ALL_MODELS    = LARGE_MODELS + SMALL_MODELS
LARGE_PROMPTS = ["wlm_sl", "wlm_json", "base_a", "base_b"]
SMALL_PROMPTS = ["wlm_sl", "base_a", "base_b"]
DIMS          = ["claude_structure", "claude_hallucination", "claude_completeness"]
SHORT         = {"claude_structure": "s", "claude_hallucination": "h",
                 "claude_completeness": "c"}

MODEL_LABELS  = {
    "claude":      "Claude",
    "gpt-4o":      "GPT-4o",
    "gpt-4o-mini": "GPT-4o-mini",
    "qwen-7b":     "Qwen2.5-7B",
    "gemma-4b":    "Gemma3-4B",
}
PROMPT_LABELS = {
    "wlm_sl":   "WLM-SL",
    "wlm_json": "WLM-JSON",
    "base_a":   "Baseline A",
    "base_b":   "Baseline B",
}
COLORS = {
    "wlm_sl":   "#2E75B6",
    "wlm_json": "#70AD47",
    "base_a":   "#ED7D31",
    "base_b":   "#FFC000",
}


def valid(df, j="claude"):
    return df[df[f"{j}_parse_error"].astype(str).str.lower() != "true"]


def cohen_d_ci(a, b, n_boot=5000, seed=42):
    a, b = np.array(a, float), np.array(b, float)
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan"), float("nan")
    pool = math.sqrt(
        ((len(a)-1)*np.std(a,ddof=1)**2 + (len(b)-1)*np.std(b,ddof=1)**2)
        / (len(a)+len(b)-2)
    )
    obs = (np.mean(a)-np.mean(b)) / pool if pool else float("nan")
    np.random.seed(seed)
    boots = []
    for _ in range(n_boot):
        ba = np.random.choice(a, len(a), replace=True)
        bb = np.random.choice(b, len(b), replace=True)
        p  = math.sqrt(((len(ba)-1)*np.std(ba,ddof=1)**2 +
                         (len(bb)-1)*np.std(bb,ddof=1)**2)
                        /(len(ba)+len(bb)-2))
        boots.append((np.mean(ba)-np.mean(bb))/p if p else 0)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return obs, lo, hi


# ── Summary table ─────────────────────────────────────────────────────────────

def summary_table(df, tag):
    vdf = valid(df)
    print("\n" + "="*80)
    print("EXP2 SUMMARY  (Claude judge, mean ± SE, domain-independent tasks T08-T37)")
    print("="*80)
    print(f"{'model/prompt':38s} {'h':>6} {'±SE':>5} {'s':>6} {'c':>6} "
          f"{'η':>6} {'Δ':>6} {'n':>4}")
    print("-"*80)
    records = []
    for m in ALL_MODELS:
        prompts = LARGE_PROMPTS if m in LARGE_MODELS else SMALL_PROMPTS
        for p in prompts:
            sub = vdf[(vdf.model_key==m) & (vdf.prompt_key==p)]
            if len(sub) == 0: continue
            h = sub["claude_hallucination"].values
            s = sub["claude_structure"].values
            c = sub["claude_completeness"].values
            tok = sub["output_tokens"].values
            mu  = (sub["claude_structure"]+sub["claude_hallucination"]+
                   sub["claude_completeness"])/3
            eta = (mu / np.log(tok.clip(1)+1)).mean()
            d   = sub["agreement_mean_diff"].mean()
            n   = len(sub)
            se  = np.std(h,ddof=1)/math.sqrt(n) if n>1 else 0
            print(f"  {m+'/'+p:36s} "
                  f"{np.mean(h):6.3f} ±{se:4.3f} "
                  f"{np.mean(s):6.3f} {np.mean(c):6.3f} "
                  f"{eta:6.3f} {d:6.3f} {n:4d}")
            records.append(dict(model=m, prompt=p,
                                h_mean=np.mean(h), h_se=se,
                                s_mean=np.mean(s), c_mean=np.mean(c),
                                eta=eta, delta=d, n=n))
        print()
    return pd.DataFrame(records)


# ── Cohen d table ─────────────────────────────────────────────────────────────

def cohen_table(df):
    vdf = valid(df)
    print("\n" + "="*80)
    print("COHEN d  (hallucination vs base_a, bootstrapped 95% CI)")
    print("="*80)
    results = []
    for m in ALL_MODELS:
        ba = vdf[(vdf.model_key==m)&(vdf.prompt_key=="base_a")]["claude_hallucination"].values
        if len(ba) < 2: continue
        prompts = ["wlm_sl","wlm_json"] if m in LARGE_MODELS else ["wlm_sl"]
        for p in prompts:
            wp = vdf[(vdf.model_key==m)&(vdf.prompt_key==p)]["claude_hallucination"].values
            if len(wp) < 2: continue
            d, lo, hi = cohen_d_ci(wp, ba)
            sig = " *" if lo > 0 else ""
            print(f"  {m:15s}/{p:10s}: d={d:+.3f} [{lo:+.3f}, {hi:+.3f}]{sig}")
            results.append(dict(model=m, prompt=p, d=d, ci_lo=lo, ci_hi=hi))
        print()
    return pd.DataFrame(results)


# ── Per task-type breakdown ───────────────────────────────────────────────────

def task_type_breakdown(df):
    vdf = valid(df)
    print("\n" + "="*80)
    print("PER TASK-TYPE  (hallucination mean, WLM-SL vs Baseline A)")
    print("="*80)
    task_types = vdf["task_type"].unique()
    for tt in sorted(task_types):
        sub = vdf[vdf.task_type==tt]
        print(f"\n  {tt}")
        for m in ["claude","gpt-4o"]:
            for p in ["wlm_sl","base_a"]:
                s = sub[(sub.model_key==m)&(sub.prompt_key==p)]["claude_hallucination"]
                if len(s): print(f"    {m:10s}/{p:8s}: h={s.mean():.2f} (n={len(s)})")


# ── Figures ───────────────────────────────────────────────────────────────────

def make_figures(df, tag, summ_df):
    vdf = valid(df)

    # Fig 1: hallucination by model × format (bar chart)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Exp2: Hallucination Suppression — T08–T37 (Claude judge)", fontsize=12)

    for ax, models, title in [
        (axes[0], LARGE_MODELS,  "Large Models"),
        (axes[1], SMALL_MODELS,  "Small Models"),
    ]:
        prompts = LARGE_PROMPTS if models == LARGE_MODELS else SMALL_PROMPTS
        x     = np.arange(len(models))
        width = 0.8 / len(prompts)
        for i, p in enumerate(prompts):
            means, errs = [], []
            for m in models:
                sub = vdf[(vdf.model_key==m)&(vdf.prompt_key==p)]["claude_hallucination"]
                means.append(sub.mean() if len(sub) else 0)
                errs.append(sub.sem() if len(sub)>1 else 0)
            offset = (i - len(prompts)/2 + 0.5) * width
            ax.bar(x+offset, means, width*0.9, yerr=errs,
                   label=PROMPT_LABELS.get(p,p),
                   color=COLORS.get(p,"#999"),
                   capsize=3)
        ax.set_xticks(x)
        ax.set_xticklabels([MODEL_LABELS.get(m,m) for m in models], fontsize=9)
        ax.set_ylim(0, 5.5)
        ax.set_ylabel("Hallucination suppression (1–5)")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.axhline(y=4, color="green", linestyle="--", alpha=0.3, linewidth=0.8)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig1_bar.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")

    # Fig 2: Cohen d heatmap for large models
    fig, ax = plt.subplots(figsize=(7, 4))
    models  = LARGE_MODELS
    prompts = ["wlm_sl", "wlm_json"]
    mat = np.zeros((len(models), len(prompts)))
    for mi, m in enumerate(models):
        ba = vdf[(vdf.model_key==m)&(vdf.prompt_key=="base_a")]["claude_hallucination"].values
        for pi, p in enumerate(prompts):
            wp = vdf[(vdf.model_key==m)&(vdf.prompt_key==p)]["claude_hallucination"].values
            if len(wp)>=2 and len(ba)>=2:
                d, _, _ = cohen_d_ci(wp, ba, n_boot=1000)
                mat[mi, pi] = d
    im = ax.imshow(mat, cmap="RdYlGn", vmin=-1.5, vmax=1.5)
    ax.set_xticks(range(len(prompts)))
    ax.set_xticklabels([PROMPT_LABELS[p] for p in prompts])
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([MODEL_LABELS[m] for m in models])
    for i in range(len(models)):
        for j in range(len(prompts)):
            ax.text(j, i, f"{mat[i,j]:+.2f}", ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if abs(mat[i,j])>0.8 else "black")
    plt.colorbar(im, ax=ax, label="Cohen's d vs Baseline A")
    ax.set_title("Exp2: Cohen's d — Hallucination (Large Models)")
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig2_cohend.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")

    # Fig 3: per-task-type hallucination heatmap (all models, wlm_sl vs base_a)
    task_types = sorted(vdf["task_type"].unique())
    models_all = ALL_MODELS
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Exp2: Per-Task-Type Hallucination (h) — WLM-SL vs Baseline A", fontsize=11)
    for ax, prompt, title in [
        (axes[0], "wlm_sl",  "WLM-SL"),
        (axes[1], "base_a",  "Baseline A"),
    ]:
        mat = np.full((len(models_all), len(task_types)), np.nan)
        for mi, m in enumerate(models_all):
            for ti, tt in enumerate(task_types):
                sub = vdf[(vdf.model_key==m)&(vdf.prompt_key==prompt)&
                           (vdf.task_type==tt)]["claude_hallucination"]
                if len(sub): mat[mi, ti] = sub.mean()
        im = ax.imshow(mat, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")
        ax.set_xticks(range(len(task_types)))
        ax.set_xticklabels([t.replace("_","\n") for t in task_types], fontsize=7)
        ax.set_yticks(range(len(models_all)))
        ax.set_yticklabels([MODEL_LABELS.get(m,m) for m in models_all], fontsize=8)
        ax.set_title(title)
        for mi in range(len(models_all)):
            for ti in range(len(task_types)):
                v = mat[mi,ti]
                if not np.isnan(v):
                    c = "white" if v<2.5 or v>4.2 else "black"
                    ax.text(ti, mi, f"{v:.1f}", ha="center", va="center",
                            fontsize=7, fontweight="bold", color=c)
        if prompt == "base_a":
            plt.colorbar(im, ax=ax, shrink=0.8, label="h (1–5)")
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig3_heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


# ── Exp1 vs Exp2 comparison ───────────────────────────────────────────────────

def compare_exp1(exp2_df, exp1_tag):
    exp1_path = RESULTS_DIR / f"{exp1_tag}_scores.csv"
    if not exp1_path.exists():
        print(f"  Exp1 file not found: {exp1_path}")
        return
    exp1 = pd.read_csv(exp1_path)
    exp2 = exp2_df.copy()

    print("\n" + "="*80)
    print("EXP1 vs EXP2  (WLM-SL hallucination: T01–T07 vs T08–T37)")
    print("="*80)
    vexp1 = exp1[exp1["claude_parse_error"].astype(str).str.lower()!="true"]
    vexp2 = exp2[exp2["claude_parse_error"].astype(str).str.lower()!="true"]

    for m in ["claude", "gpt-4o"]:
        for p in ["wlm_sl", "base_a"]:
            h1 = vexp1[(vexp1.model_key==m)&(vexp1.prompt_key==p)]["claude_hallucination"]
            h2 = vexp2[(vexp2.model_key==m)&(vexp2.prompt_key==p)]["claude_hallucination"]
            if len(h1) and len(h2):
                print(f"  {m:10s}/{p:8s}: "
                      f"Exp1={h1.mean():.3f}(n={len(h1)}) "
                      f"Exp2={h2.mean():.3f}(n={len(h2)}) "
                      f"diff={h2.mean()-h1.mean():+.3f}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="WLM Experiment 2 Analyzer")
    parser.add_argument("--tag",         required=True, help="exp2 output tag")
    parser.add_argument("--compare-exp1", default="", help="Exp1 tag for comparison")
    args = parser.parse_args()

    csv_path = RESULTS_DIR / f"{args.tag}_scores.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path.name}")
    print(f"Models:  {sorted(df.model_key.unique())}")
    print(f"Prompts: {sorted(df.prompt_key.unique())}")
    print(f"Tasks:   {sorted(df.task_id.unique())}")

    summ = summary_table(df, args.tag)
    cd   = cohen_table(df)
    task_type_breakdown(df)

    print("\nGenerating figures...")
    make_figures(df, args.tag, summ)

    if args.compare_exp1:
        compare_exp1(df, args.compare_exp1)

    # Save tables
    summ.to_csv(RESULTS_DIR / f"{args.tag}_summary.csv", index=False)
    cd.to_csv(RESULTS_DIR / f"{args.tag}_cohend.csv", index=False)
    print(f"\n  Summary → {args.tag}_summary.csv")
    print(f"  Cohen d → {args.tag}_cohend.csv")


if __name__ == "__main__":
    main()
