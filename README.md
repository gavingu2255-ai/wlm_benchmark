# WLM D/E/S Benchmark

Replication code, prompt definitions, task specifications, and raw scoring data for the paper:

**D/E/S: A Tri-Layer Generative Prompt Architecture for Structured Reasoning and Hallucination Suppression in LLMs**
Wujie Gu (2026)

This repository contains everything needed to reproduce the ~1,000-run benchmark across six models, five prompt formats, and three experiments (WLM-content, domain-independent, and adversarial stress test).

---

## What's in here

```
.
├── analyze.py              # Experiment 1 analysis & figures
├── analyze_exp2.py         # Experiment 2 analysis & figures
├── runner.py               # Core Claude + GPT-4o evaluation runner
├── run_exp2.py             # Experiment 2 runner (T08–T37)
├── run_exp3.py             # Experiment 3 runner (T38–T52)
├── run_gemini.py           # Gemini 2.5 Flash runner (all three experiments)
├── config.py               # Experiment/model/prompt configuration
├── requirements.txt        # Python dependencies
│
├── prompts/                # Five prompt format implementations
│   ├── baseline_a.py       # Raw task prompt, no scaffolding
│   ├── baseline_b.py       # Structured Chain-of-Thought
│   ├── wlm_hybrid_v2.py    # 7-field flat JSON (primary D/E/S format)
│   ├── wlm_sl.py           # Line-level slot tags (REQ/COND/EXCL/CONST/SEQ)
│   └── wlm_json.py         # Strict JSON with nested schema
│
├── tasks/                  # 52 benchmark task specifications
├── models/                 # Model API wrappers (Claude, GPT-4o, Gemini, Qwen, Gemma)
├── scoring/                # Dual LLM-as-judge scoring (Claude + GPT-4o)
├── data/                   # Raw outputs and judge scores (CSV)
├── exp 2/                  # Experiment 2 working files
└── exp 3/                  # Experiment 3 working files
```

**Heads-up on repo state.** This is the working benchmark, not a polished release. File organisation is loose — Experiment 2 and 3 outputs live under `exp 2/` and `exp 3/` (with spaces in folder names; Windows artefact). The runners share a lot of duplicated logic with `runner.py` that wasn't refactored. Everything works; nothing is pretty. Clean-up is on the list, but the data is final.

---

## Reproducing the benchmark

### 1. Setup

```bash
pip install -r requirements.txt
```

API keys required (set as environment variables):

```bash
export ANTHROPIC_API_KEY=...     # Claude (agent + judge)
export OPENAI_API_KEY=...        # GPT-4o (agent + judge)
export GOOGLE_API_KEY=...        # Gemini 2.5 Flash (agent only)
export TOGETHER_API_KEY=...      # Qwen2.5-7B, Gemma3-4B (open-weight agents)
```

### 2. Run experiments

```bash
# Experiment 1 — Format selection study (T01–T07, 7 WLM-content tasks)
python runner.py --exp 1

# Experiment 2 — Domain-independent generalization (T08–T37, 30 tasks)
python run_exp2.py

# Experiment 3 — Adversarial stress test (8 of 15 tasks)
python run_exp3.py

# Gemini 2.5 Flash across all three experiments
python run_gemini.py --exp 1 --tag gemini_all
python run_gemini.py --exp 2 --tag gemini_all --resume
python run_gemini.py --exp 3 --tag gemini_all --resume
```

`--resume` skips conditions already in the output CSV. Use it after API failures (503s during the Gemini runs are common — the runners log failures and continue).

### 3. Analyse

```bash
python analyze.py            # Experiment 1: Cohen's d, judge agreement, figures
python analyze_exp2.py       # Experiment 2: same, n=30
```

Outputs include all 12 figures from the paper and the underlying statistics (mean h/s/c, Δh, Cohen's d with bootstrapped 95% CIs).

---

## Models evaluated

| Tier | Model | Provider | Used as |
|---|---|---|---|
| Frontier | Claude Sonnet | Anthropic | Agent + judge |
| Frontier | GPT-4o | OpenAI | Agent + judge |
| Frontier | Gemini 2.5 Flash | Google | Agent only |
| Mid | GPT-4o-mini | OpenAI | Agent only |
| Sub-10B | Qwen2.5-7B | Alibaba (Together) | Agent only |
| Sub-10B | Gemma3-4B | Google DeepMind (Together) | Agent only |

All evaluations use temperature 0 with default sampling. No fine-tuning. No few-shot examples beyond the prompt template.

---

## What gets measured

Every output is scored on a 1–5 integer scale across three dimensions by two independent judges (Claude Sonnet and GPT-4o):

- **h** — Hallucination suppression (primary outcome)
- **s** — Structure coherence
- **c** — Completeness

Derived metrics:

- **η = μ / ln(τ + 1)** — Token efficiency, where μ is the mean score and τ is output token count
- **Δh = |h_Claude − h_GPT|** — Judge disagreement on hallucination specifically; primary validity indicator in the paper
- **Cohen's d** — Effect size vs Baseline A, with bootstrapped 95% CIs (5,000 resamples)

The composite metric Δ = (|s_diff| + |h_diff| + |c_diff|) / 3 is also computed and reported in Appendix C of the paper as a robustness check.

---

## Data files

Raw CSVs in `data/`:

- `exp1_scores.csv` — 210 runs (5 large models × 3–5 formats × 7 tasks)
- `exp2_scores.csv` — 720 runs (6 models × 3–5 formats × 30 tasks)
- `exp3_scores.csv` — 88 runs (2 large models × 3 formats × 8 tasks + Gemini × 5 × 8)
- `gemini_all_scores.csv` — All Gemini runs across the three experiments

Each row contains agent output, both judge scores, token counts, latency, and computed metrics. Approximately 1,018 total runs.

---

## Notes on reproducibility

Bootstrapped CIs use `numpy.random.seed(42)` for reproducible resampling. Judge scoring is at temperature 0 but LLM judges are not strictly deterministic — running the scoring step again may shift individual cells by ±1 on the 1–5 scale. Aggregate effects (Cohen's d, ★ confirmations) are stable across re-runs.

Gemini 2.5 Flash occasionally returns 503 errors during long batches. The runners catch these, log them, and continue. Use `--resume` to fill in missed conditions.

---

## License

Code: MIT
Data and prompts: CC BY-NC-ND 4.0

Cite as:

> Gu, W. (2026). D/E/S: A Tri-Layer Generative Prompt Architecture for Structured Reasoning and Hallucination Suppression in LLMs. *Frontiers in Artificial Intelligence* (under review). https://github.com/gavingu2255-ai/wlm-des-benchmark

---

## Contact

Issues and replication questions: open a GitHub issue.
For the WLM framework background that motivates D/E/S, see the companion preprints on OSF (osf.io/rq5vj) and ResearchGate.
