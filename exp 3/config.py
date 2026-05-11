# config.py  —  WLM Benchmark: Central Configuration
# All model definitions, prompt names, and experiment parameters in one place.

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).parent
DATA_DIR    = ROOT_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"
FIGURES_DIR = DATA_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Judge models ───────────────────────────────────────────────────────────────
JUDGES = {
    "claude": {
        "api":      "anthropic",
        "model_id": "claude-sonnet-4-20250514",
        "max_tokens": 700,
    },
    "gpt4o": {
        "api":      "openai",
        "model_id": "gpt-4o",
        "max_tokens": 700,
    },
}

# ── Model registry ─────────────────────────────────────────────────────────────
# key = short name used in CLI and output filenames
MODELS = {
    "gemini-pro": {
        "api":        "gemini",
        "model_id":   "gemini-1.5-pro",
        "max_tokens": 2048,
        "label":      "Gemini 1.5 Pro",
        "tier":       "large",
    },
    "claude": {
        "api":        "anthropic",
        "model_id":   "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "label":      "Claude Sonnet 4.5",
        "tier":       "large",
    },
    "gpt-4o": {
        "api":        "openai",
        "model_id":   "gpt-4o",
        "max_tokens": 2048,
        "label":      "GPT-4o",
        "tier":       "large",
    },
    "gpt-4o-mini": {
        "api":        "openai",
        "model_id":   "gpt-4o-mini",
        "max_tokens": 2048,
        "label":      "GPT-4o-mini",
        "tier":       "medium",
    },
    "qwen-7b": {
        "api":        "ollama",
        "model_id":   "qwen2.5:7b",
        "max_tokens": 2048,
        "label":      "Qwen2.5 7B",
        "tier":       "small",
    },
    "gemma-4b": {
        "api":        "ollama",
        "model_id":   "gemma3:4b",
        "max_tokens": 2048,
        "label":      "Gemma 3 4B",
        "tier":       "small",
    },
}

# ── Prompt registry ────────────────────────────────────────────────────────────
PROMPTS = {
    "wlm_json":      "WLM D/E/S (JSON output)",
    "wlm_sl":        "WLM D/E/S (SL line format)",
    "wlm_hybrid_v2": "WLM Hybrid v2 (structure + completeness_check)",
    "base_a":        "Baseline A — Raw LLM",
    "base_b":        "Baseline B — Structured CoT",
}

# ── Experiment defaults ────────────────────────────────────────────────────────
DEFAULT_MODELS  = list(MODELS.keys())
DEFAULT_PROMPTS = list(PROMPTS.keys())
DEFAULT_TASKS   = ["T01","T02","T03","T04","T05","T06","T07"]
DEFAULT_JUDGES  = list(JUDGES.keys())

OLLAMA_URL = "http://localhost:11434/api/chat"

# ── Experiment 2 configuration ─────────────────────────────────────────────────
# T08-T37: 30 domain-independent tasks
# Large models: wlm_sl + wlm_json + base_a + base_b  (4 formats)
# Small models: wlm_sl + base_a + base_b              (3 formats)

EXP1_LARGE_MODELS  = ["claude", "gpt-4o", "gemini-pro"]
EXP1_LARGE_PROMPTS = ["wlm_json", "wlm_sl", "wlm_hybrid_v2", "base_a", "base_b"]
# Gemini补跑: 1 × 5 × 7 = 35条



EXP2_LARGE_MODELS  = ["claude", "gpt-4o", "gemini-pro"]
EXP2_SMALL_MODELS  = ["gpt-4o-mini", "qwen-7b", "gemma-4b"]
EXP2_LARGE_PROMPTS = ["wlm_sl", "wlm_json", "wlm_hybrid_v2", "base_a", "base_b"]
EXP2_SMALL_PROMPTS = ["wlm_sl", "base_a", "base_b"]

# Total runs:
# Large: 2 models × 4 prompts × 30 tasks = 240
# Small: 3 models × 3 prompts × 30 tasks = 270
# Total: 510 runs × 2 judges = 1020 judge calls

# ── Experiment 3 configuration ─────────────────────────────────────────────────
# T38-T52: 15 stress-test tasks
# Conflicting information (T38-T41): model must identify conflict, refuse to resolve
# Information gap (T42-T45): model must flag missing data, say "cannot determine"
# High structural load (T46-T49): multi-constraint, internal consistency required
# Adversarial framing (T50-T52): question nudges toward wrong answer

EXP3_TASKS_IDS    = ["T38","T41","T42","T44","T46","T50","T51","T52"]
EXP3_LARGE_MODELS  = ["claude", "gpt-4o"]
EXP3_SMALL_MODELS  = []
EXP3_LARGE_PROMPTS = ["wlm_hybrid_v2", "base_a", "base_b"]
EXP3_SMALL_PROMPTS = []

# Total runs:
# Large: 2 × 3 × 8 = 48
# Small: none
# Total: 48 runs × 2 judges = 96 judge calls
