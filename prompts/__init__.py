# prompts/__init__.py  —  Prompt registry

from prompts.wlm_json      import WLM_JSON_PROMPT
from prompts.wlm_sl        import WLM_SL_PROMPT
from prompts.wlm_hybrid    import WLM_HYBRID_PROMPT, WLM_HYBRID_V2_PROMPT
from prompts.baseline_a    import BASELINE_A_PROMPT
from prompts.baseline_b    import BASELINE_B_PROMPT

PROMPT_MAP = {
    "wlm_json":      WLM_JSON_PROMPT,
    "wlm_sl":        WLM_SL_PROMPT,
    "wlm_hybrid":    WLM_HYBRID_PROMPT,       # v1 alias → points to v2 internally
    "wlm_hybrid_v2": WLM_HYBRID_V2_PROMPT,    # explicit v2
    "base_a":        BASELINE_A_PROMPT,
    "base_b":        BASELINE_B_PROMPT,
}

HYBRID_PROMPTS = {"wlm_hybrid", "wlm_hybrid_v2"}

def get_prompt(prompt_key: str, task_injection: str = "",
               hybrid_injection: str = "") -> str:
    """
    Return system prompt for the given key.
    task_injection:   appended for all prompt types (e.g. T04 analogy rules).
    hybrid_injection: appended only for hybrid prompt types (field mapping hints).
    """
    base = PROMPT_MAP[prompt_key]
    sep  = "\n\n" + "━"*37 + "\nTASK-SPECIFIC RULES\n" + "━"*37 + "\n"

    if task_injection:
        base = base + sep + task_injection

    if hybrid_injection and prompt_key in HYBRID_PROMPTS:
        base = base + "\n\n" + "━"*37 + "\nHYBRID FIELD MAPPING FOR THIS TASK\n" + "━"*37 + "\n" + hybrid_injection

    return base
