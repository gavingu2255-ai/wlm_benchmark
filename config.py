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
