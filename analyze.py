#!/usr/bin/env python3
# analyze.py  —  WLM Benchmark Analysis
# Reads any scores CSV and generates publication-ready figures + summary tables.
#
# Usage:
#   python analyze.py                          # latest run in data/results/
#   python analyze.py --tag hybrid_v1         # specific run
#   python analyze.py --tag run_1234,run_5678 # merge multiple runs

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats as sp_stats

matplotlib.rcParams.update({
    "font.family":    "DejaVu Sans",
    "font.size":      10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "savefig.dpi":    300,
    "figure.dpi":     140,
})

from config import RESULTS_DIR, FIGURES_DIR, MODELS, PROMPTS

# ── Visual identity ───────────────────────────────────────────────────────────

MODEL_COLORS = {
    "claude":      "#1D4ED8",
    "gpt-4o":      "#16A34A",
    "gpt-4o-mini": "#D97706",
    "qwen-7b":     "#DC2626",
    "gemma-4b":    "#7C3AED",
}
PROMPT_COLORS = {
    "wlm_json":   "#1D4ED8",
    "wlm_sl":     "#16A34A",
    "wlm_hybrid": "#7C3AED",
    "base_a":     "#DC2626",
    "base_b":     "#D97706",
}
PROMPT_LABELS = {
    "wlm_json":   "WLM-JSON",
    "wlm_sl":     "WLM-SL",
    "wlm_hybrid": "WLM-Hybrid",
    "base_a":     "Baseline A",
    "base_b":     "Baseline B",
}
MODEL_LABELS = {k: MODELS[k]["label"] for k in MODELS}

QUALITY_DIMS   = ["claude_structure", "claude_hallucination", "claude_completeness"]
DIM_LABELS     = {
    "claude_structure":        "Structure",
    "claude_hallucination":    "Hallucination\nSuppression",
    "claude_completeness":     "Completeness",
    "claude_token_efficiency": "Token\nEfficiency η",
}

# Primary judge for main analysis
PRIMARY   = "claude"
SECONDARY = "gpt4o"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data(tags: list[str]) -> pd.DataFrame:
    frames = []
    for tag in tags:
        pattern = f"*{tag}*_scores.csv" if tag else "*_scores.csv"
        files   = sorted(RESULTS_DIR.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No scores CSV found for tag '{tag}' in {RESULTS_DIR}")
        # Use most recent if multiple
        f = files[-1]
        print(f"  Loading: {f.name}")
        frames.append(pd.read_csv(f))
    df = pd.concat(frames, ignore_index=True)

    # Ensure numeric cols
    num_cols = [c for c in df.columns if any(x in c for x in
                ["structure","hallucination","completeness","efficiency","tokens","latency","diff"])]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


# ── Stats helpers ─────────────────────────────────────────────────────────────

def ci95(x):
    x = np.array(x, float)
    n = len(x)
    if n < 2:
        return np.mean(x), np.mean(x), np.mean(x)
    se = sp_stats.sem(x)
    lo, hi = sp_stats.t.interval(0.95, df=n-1, loc=np.mean(x), scale=se)
    return np.mean(x), lo, hi

def cohen_d(a, b):
    a, b = np.array(a, float), np.array(b, float)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pool = np.sqrt(((len(a)-1)*np.std(a,ddof=1)**2 +
                    (len(b)-1)*np.std(b,ddof=1)**2) / (len(a)+len(b)-2))
    return (np.mean(a)-np.mean(b))/pool if pool else float("nan")

def compute_eta(df: pd.DataFrame, judge: str = "claude") -> pd.Series:
    """Compute token efficiency using specified judge's scores.
    Rows with parse_error=True for that judge are set to NaN.
    """
    ok  = df[f"{judge}_parse_error"].astype(str).str.lower() != "true"
    s   = df[f"{judge}_structure"]
    h   = df[f"{judge}_hallucination"]
    c   = df[f"{judge}_completeness"]
    mu  = (s + h + c) / 3.0
    tok = df["output_tokens"].clip(lower=1)
    eta = mu / np.log(tok + 1)
    eta[~ok] = np.nan
    return eta


def _valid(df: pd.DataFrame, judge: str = "claude") -> pd.DataFrame:
    """Filter to rows where the given judge did not have a parse error."""
    mask = df[f"{judge}_parse_error"].astype(str).str.lower() != "true"
    return df[mask]


# ── Print summary ─────────────────────────────────────────────────────────────

def print_summary(df: pd.DataFrame):
    models  = df["model_key"].unique()
    prompts = df["prompt_key"].unique()

    print("\n" + "="*85)
    print("SUMMARY: Claude judge scores (parse_error rows excluded)")
    print(f"  {'model/prompt':35s} {'s':>6} {'h':>6} {'c':>6} {'η':>8} {'tok':>6} {'Δ':>6} {'n':>4}")
    print("="*85)

    for m in models:
        for p in prompts:
            sub = _valid(df[(df["model_key"]==m) & (df["prompt_key"]==p)])
            if len(sub)==0: continue
            s   = sub["claude_structure"].mean()
            h   = sub["claude_hallucination"].mean()
            c   = sub["claude_completeness"].mean()
            eta = compute_eta(sub).mean()
            tok = sub["output_tokens"].mean()
            dlt = sub["agreement_mean_diff"].mean()
            n   = len(sub)
            label = f"{m}/{p}"
            print(f"  {label:35s} {s:6.2f} {h:6.2f} {c:6.2f} {eta:8.3f} {tok:6.0f} {dlt:6.3f} {n:4d}")
        print()

    # GPT-4o judge validation
    print("GPT-4o judge validation (parse_error rows excluded):")
    print(f"  {'model/prompt':35s} {'s':>6} {'h':>6} {'c':>6} {'n_ok':>6}")
    for m in models:
        for p in prompts:
            sub_ok = _valid(df[(df["model_key"]==m)&(df["prompt_key"]==p)], "gpt4o")
            sub_all = df[(df["model_key"]==m)&(df["prompt_key"]==p)]
            if len(sub_ok)==0: continue
            n_err = len(sub_all) - len(sub_ok)
            label = f"{m}/{p}"
            print(f"  {label:35s} "
                  f"{sub_ok['gpt4o_structure'].mean():6.2f} "
                  f"{sub_ok['gpt4o_hallucination'].mean():6.2f} "
                  f"{sub_ok['gpt4o_completeness'].mean():6.2f} "
                  f"  {len(sub_ok):3d}/{len(sub_all)}"
                  f"{'  ⚠ '+str(n_err)+' parse errors' if n_err else ''}")
        print()

    # Cohen d: WLM formats vs base_a on hallucination (Claude judge)
    print("\nCOHEN d — hallucination Claude judge (WLM vs Baseline A):")
    for m in models:
        ba = _valid(df[(df["model_key"]==m)&(df["prompt_key"]=="base_a")])["claude_hallucination"]
        for p in [p for p in prompts if p.startswith("wlm")]:
            wp = _valid(df[(df["model_key"]==m)&(df["prompt_key"]==p)])["claude_hallucination"]
            if len(wp)>1 and len(ba)>1:
                d = cohen_d(wp.values, ba.values)
                print(f"  {m:15s} / {p:12s} vs base_a:  d={d:+.3f}")
    print()


# ── Figure 1: Bar chart — quality dimensions by model × prompt ────────────────

def fig_quality_bars(df: pd.DataFrame, tag: str):
    models  = [m for m in MODEL_COLORS if m in df["model_key"].values]
    prompts = [p for p in PROMPT_COLORS if p in df["prompt_key"].values]
    dims    = QUALITY_DIMS
    n_p     = len(prompts)
    width   = 0.14
    x       = np.arange(len(dims))

    fig, axes = plt.subplots(1, len(models), figsize=(4*len(models), 5), sharey=True)
    if len(models)==1: axes = [axes]

    for ax, model in zip(axes, models):
        offsets = np.linspace(-(n_p-1)/2, (n_p-1)/2, n_p) * width
        for i, prompt in enumerate(prompts):
            sub = df[(df["model_key"]==model) & (df["prompt_key"]==prompt)]
            if len(sub)==0: continue
            vals, lo_e, hi_e = [], [], []
            for d in dims:
                m_v, lo, hi = ci95(sub[d].dropna())
                vals.append(m_v); lo_e.append(m_v-lo); hi_e.append(hi-m_v)
            bars = ax.bar(x + offsets[i], vals, width,
                          label=PROMPT_LABELS.get(prompt, prompt),
                          color=PROMPT_COLORS.get(prompt,"gray"),
                          alpha=0.83, edgecolor="white", linewidth=0.4)
            ax.errorbar(x + offsets[i], vals, yerr=[lo_e, hi_e],
                        fmt="none", color="black", capsize=2.5, linewidth=1.1)

        ax.set_xticks(x)
        ax.set_xticklabels([DIM_LABELS[d].replace("\n"," ") for d in dims],
                            fontsize=8, rotation=10, ha="right")
        ax.set_ylim(0, 6.0)
        ax.set_title(MODEL_LABELS.get(model, model), fontsize=10)
        ax.spines[["top","right"]].set_visible(False)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("Score (1–5, consensus mean ± 95% CI)", fontsize=9)
    handles = [mpatches.Patch(facecolor=PROMPT_COLORS.get(p,"gray"), alpha=0.83,
                               label=PROMPT_LABELS.get(p,p)) for p in prompts]
    fig.legend(handles=handles, loc="lower center", ncol=len(prompts),
               fontsize=8.5, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Figure 1: Quality Scores by Model and Prompt Architecture",
                 fontsize=11, y=1.01)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig1_quality_bars.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Fig 1 → {path.name}")


# ── Figure 2: Token efficiency η by model × prompt ───────────────────────────

def fig_token_efficiency(df: pd.DataFrame, tag: str):
    df = df.copy()
    df["eta"] = compute_eta(df)

    models  = [m for m in MODEL_COLORS if m in df["model_key"].values]
    prompts = [p for p in PROMPT_COLORS if p in df["prompt_key"].values]
    x       = np.arange(len(models))
    width   = 0.14
    n_p     = len(prompts)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: η score
    ax = axes[0]
    offsets = np.linspace(-(n_p-1)/2, (n_p-1)/2, n_p) * width
    for i, prompt in enumerate(prompts):
        vals, lo_e, hi_e = [], [], []
        for model in models:
            sub = df[(df["model_key"]==model) & (df["prompt_key"]==prompt)]["eta"].dropna()
            m_v, lo, hi = ci95(sub) if len(sub)>1 else (sub.mean(), sub.mean(), sub.mean())
            vals.append(m_v); lo_e.append(m_v-lo); hi_e.append(hi-m_v)
        bars = ax.bar(x + offsets[i], vals, width,
                      label=PROMPT_LABELS.get(prompt, prompt),
                      color=PROMPT_COLORS.get(prompt,"gray"),
                      alpha=0.83, edgecolor="white", linewidth=0.4)
        ax.errorbar(x + offsets[i], vals, yerr=[lo_e, hi_e],
                    fmt="none", color="black", capsize=2.5, linewidth=1.1)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=6.5)

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS.get(m,m) for m in models],
                        fontsize=8.5, rotation=12, ha="right")
    ax.set_ylabel("η = mean_quality / ln(output_tokens + 1)", fontsize=9)
    ax.set_title("Token Efficiency η (mean ± 95% CI)", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.spines[["top","right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    # Right: output token count
    ax2 = axes[1]
    for i, prompt in enumerate(prompts):
        vals2, lo_e2, hi_e2 = [], [], []
        for model in models:
            sub = df[(df["model_key"]==model) & (df["prompt_key"]==prompt)]["output_tokens"].dropna()
            m_v, lo, hi = ci95(sub) if len(sub)>1 else (sub.mean(), sub.mean(), sub.mean())
            vals2.append(m_v); lo_e2.append(m_v-lo); hi_e2.append(hi-m_v)
        bars2 = ax2.bar(x + offsets[i], vals2, width,
                        color=PROMPT_COLORS.get(prompt,"gray"),
                        alpha=0.83, edgecolor="white", linewidth=0.4)
        ax2.errorbar(x + offsets[i], vals2, yerr=[lo_e2, hi_e2],
                     fmt="none", color="black", capsize=2.5, linewidth=1.1)

    ax2.set_xticks(x)
    ax2.set_xticklabels([MODEL_LABELS.get(m,m) for m in models],
                         fontsize=8.5, rotation=12, ha="right")
    ax2.set_ylabel("Output Tokens (mean ± 95% CI)", fontsize=9)
    ax2.set_title("Output Token Count", fontsize=10)
    ax2.spines[["top","right"]].set_visible(False)
    ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax2.set_axisbelow(True)

    fig.suptitle("Figure 2: Token Efficiency and Output Token Count by Model × Prompt",
                 fontsize=11, y=1.01)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig2_token_efficiency.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Fig 2 → {path.name}")


# ── Figure 3: Cohen d heatmap — WLM formats vs Baseline A ────────────────────

def fig_effect_size(df: pd.DataFrame, tag: str):
    models      = [m for m in MODEL_COLORS if m in df["model_key"].values]
    wlm_prompts = [p for p in PROMPT_COLORS
                   if p.startswith("wlm") and p in df["prompt_key"].values]
    dims_short  = ["structure","hallucination","completeness"]
    dim_cols    = [f"consensus_{d}" for d in dims_short]
    df_eta      = df.copy(); df_eta["eta"] = compute_eta(df_eta)

    # Build matrix: rows=dim, cols=model × wlm_prompt
    col_labels, matrix_d = [], []
    for model in models:
        for prompt in wlm_prompts:
            ba  = df[(df["model_key"]==model) & (df["prompt_key"]=="base_a")]
            wp  = df[(df["model_key"]==model) & (df["prompt_key"]==prompt)]
            if len(ba)==0 or len(wp)==0: continue
            col_labels.append(f"{MODEL_LABELS.get(model,model)}\n{PROMPT_LABELS.get(prompt,prompt)}")
            row = []
            for dc in dim_cols:
                row.append(cohen_d(wp[dc].dropna().values, ba[dc].dropna().values))
            # η effect size
            ba_eta = df_eta[(df_eta["model_key"]==model)&(df_eta["prompt_key"]=="base_a")]["eta"]
            wp_eta = df_eta[(df_eta["model_key"]==model)&(df_eta["prompt_key"]==prompt)]["eta"]
            row.append(cohen_d(wp_eta.dropna().values, ba_eta.dropna().values))
            matrix_d.append(row)

    if not matrix_d:
        print("  Fig 3 skipped — no base_a data for comparison")
        return

    matrix = np.array(matrix_d).T   # rows=dim, cols=comparisons
    row_labels = dims_short + ["token_eff_η"]

    fig, ax = plt.subplots(figsize=(max(8, len(col_labels)*1.4), 4.5))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=-2.0, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=8)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=9.5)
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            v = matrix[i,j]
            if not np.isnan(v):
                color = "white" if abs(v)>1.8 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=9, fontweight="bold", color=color)
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("Cohen's d (WLM − Baseline A)", fontsize=9)
    ax.set_title("Figure 3: Effect Size — WLM Formats vs Baseline A\n"
                 "Green = WLM advantage | Red = Baseline A advantage",
                 fontsize=10.5, pad=10)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig3_effect_size.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Fig 3 → {path.name}")


# ── Figure 4: Inter-judge agreement Δ ────────────────────────────────────────

def fig_judge_agreement(df: pd.DataFrame, tag: str):
    models  = [m for m in MODEL_COLORS if m in df["model_key"].values]
    prompts = [p for p in PROMPT_COLORS if p in df["prompt_key"].values]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x       = np.arange(len(models))
    width   = 0.14
    n_p     = len(prompts)
    offsets = np.linspace(-(n_p-1)/2, (n_p-1)/2, n_p) * width

    for i, prompt in enumerate(prompts):
        vals = []
        for model in models:
            sub = df[(df["model_key"]==model)&(df["prompt_key"]==prompt)]["agreement_mean_diff"].dropna()
            vals.append(sub.mean() if len(sub)>0 else 0)
        bars = ax.bar(x + offsets[i], vals, width,
                      label=PROMPT_LABELS.get(prompt,prompt),
                      color=PROMPT_COLORS.get(prompt,"gray"),
                      alpha=0.83, edgecolor="white", linewidth=0.4)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=7)

    ax.axhline(1.0, color="#DC2626", linewidth=1.2, linestyle="--",
               label="Δ=1.0 (1 point disagreement)")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS.get(m,m) for m in models],
                        fontsize=9, rotation=10, ha="right")
    ax.set_ylabel("Mean Inter-Judge Score Difference (Δ)", fontsize=9)
    ax.set_title("Figure 4: Inter-Judge Agreement (Claude vs GPT-4o)\n"
                 "Lower Δ = higher agreement", fontsize=10.5, pad=10)
    ax.legend(fontsize=8.5, loc="upper right")
    ax.spines[["top","right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig4_judge_agreement.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Fig 4 → {path.name}")


# ── Figure 5: η vs hallucination scatter (sweet-spot chart) ──────────────────

def fig_eta_vs_hallucination(df: pd.DataFrame, tag: str):
    """
    Each point = one (model, prompt) combination.
    x-axis = mean hallucination suppression
    y-axis = mean token efficiency η
    This shows which format achieves the best balance.
    """
    df2 = df.copy()
    df2["eta"] = compute_eta(df2)

    models  = [m for m in MODEL_COLORS if m in df2["model_key"].values]
    prompts = [p for p in PROMPT_COLORS if p in df2["prompt_key"].values]

    fig, ax = plt.subplots(figsize=(8, 6))

    for model in models:
        for prompt in prompts:
            sub = df2[(df2["model_key"]==model)&(df2["prompt_key"]==prompt)]
            if len(sub)==0: continue
            x_v = sub["claude_hallucination"].mean()
            y_v = sub["eta"].mean()
            ax.scatter(x_v, y_v,
                       color=MODEL_COLORS.get(model,"gray"),
                       marker={"wlm_json":"D","wlm_sl":"o","wlm_hybrid":"*",
                                "base_a":"s","base_b":"^"}.get(prompt,"x"),
                       s={"wlm_hybrid":180}.get(prompt, 80),
                       zorder=3, alpha=0.85,
                       edgecolors="white", linewidths=0.5)
            ax.annotate(f"{PROMPT_LABELS.get(prompt,prompt)}",
                        (x_v, y_v), textcoords="offset points",
                        xytext=(5,4), fontsize=6.5,
                        color=MODEL_COLORS.get(model,"gray"))

    ax.set_xlabel("Hallucination Suppression (consensus mean)", fontsize=10)
    ax.set_ylabel("Token Efficiency η = quality / ln(tokens + 1)", fontsize=10)
    ax.set_title("Figure 5: Quality vs Efficiency — Format Sweet-Spot Chart\n"
                 "Top-right = best; ★ = WLM-Hybrid", fontsize=10.5, pad=10)

    # Model legend
    model_handles = [mpatches.Patch(facecolor=MODEL_COLORS.get(m,"gray"), alpha=0.85,
                                     label=MODEL_LABELS.get(m,m)) for m in models]
    ax.legend(handles=model_handles, fontsize=8.5, loc="lower right")
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.25)
    plt.tight_layout()
    path = FIGURES_DIR / f"{tag}_fig5_eta_vs_hallucination.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Fig 5 → {path.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="WLM Benchmark Analyzer")
    parser.add_argument("--tag", default="",
                        help="Run tag(s), comma-separated. Default: latest CSV in results/")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tag.split(",")] if args.tag else [""]

    print("WLM Benchmark Analyzer")
    print(f"  Results dir: {RESULTS_DIR}")
    print(f"  Figures dir: {FIGURES_DIR}")
    print()

    df = load_data(tags)
    print(f"  Loaded {len(df)} records | "
          f"models: {sorted(df['model_key'].unique())} | "
          f"prompts: {sorted(df['prompt_key'].unique())}")

    print_summary(df)

    out_tag = args.tag.replace(",","_") or "latest"
    print(f"\nGenerating figures (tag: {out_tag})...")
    fig_quality_bars(df, out_tag)
    fig_token_efficiency(df, out_tag)
    fig_effect_size(df, out_tag)
    fig_judge_agreement(df, out_tag)
    fig_eta_vs_hallucination(df, out_tag)

    print(f"\nAll figures → {FIGURES_DIR}")


if __name__ == "__main__":
    main()
