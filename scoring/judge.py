# scoring/judge.py  —  Dual LLM-as-judge (Claude + GPT-4o)
# Full rubric, boundary conditions, anti-inflation rules.
# Returns scores from both judges + inter-judge agreement metrics.

import json
import math
from typing import Dict, Any

from models.caller import call_model
from config import JUDGES

# ── Rubric ────────────────────────────────────────────────────────────────────

RUBRIC = {
    "structure": {
        1: "No discernible structure; ideas in arbitrary order; no logical connections stated.",
        2: "Minimal structure; some grouping but transitions absent; dependencies implied not stated.",
        3: "Moderate structure; major sections identifiable; some dependencies explicit; one gap or inconsistency.",
        4: "Good structure; all components present; dependencies explicit; at most one minor imprecision.",
        5: "Complete explicit logical architecture; every claim traces to prior element; zero gaps.",
    },
    "hallucination": {
        1: "Severe hallucination; multiple unsupported specific claims presented as established fact.",
        2: "Significant hallucination; at least one major unsupported assertion; epistemic status misrepresented.",
        3: "Moderate hallucination; some peripheral unsupported claims; core argument correctly qualified.",
        4: "Minimal hallucination; all central claims qualified; one minor unqualified peripheral assertion.",
        5: "Zero hallucination; all claims derived, marked [CJ]/[EC], or attributed; epistemic status consistent.",
    },
    "completeness": {
        1: "< 50% of required elements addressed.",
        2: "50–74% of required elements present.",
        3: "75–89% of required elements present with appropriate depth.",
        4: "90–99% of required elements present; one minor element underdeveloped.",
        5: "100% of required elements addressed with specified depth; nothing skipped.",
    },
}

JUDGE_SYSTEM = """You are a rigorous peer-review evaluator for a scientific study comparing AI reasoning architectures.
Score AI-generated responses on explicit rubrics. Return ONLY valid JSON. No preamble. No markdown.

STRICTNESS RULES:
1. Apply the rubric literally. If a level's boundary condition is not met, assign the lower score.
2. Do NOT reward stylistic similarity to your own outputs.
3. Do NOT reward length. Short responses meeting rubric criteria score equal to verbose ones.
4. Missing required epistemic markers ([SP]/[CJ]/[EC] or [UNCERTAIN]/[ESTABLISHED]/[THEORETICAL]) count as hallucination violations.
5. Scores of 4–5 require zero detectable defects at that level's boundary condition.
6. For each score, state WHY the next higher score was NOT assigned.

HYBRID FORMAT RULE (applies when response contains [COMPLETENESS CHECK] section):
7. For completeness scoring: the [COMPLETENESS CHECK] field must contain AT LEAST 3 specific
   ✓/✗ lines that reference actual content from the response.
   A generic statement such as "all requirements met" or "covered all elements" without
   specific references counts as completeness_check = absent → completeness score ≤ 3.
   Each ✓ line must name a specific required element AND state where it appears.
8. For structure scoring: if the response contains a [STRUCTURE] field, check that it uses
   parallel syntactic form across all listed items. Non-parallel structure = score ≤ 3."""

JUDGE_PROMPT = """Score the following AI response on three dimensions.

TASK TYPE: {task_type}
TASK INPUT: {task_input}
TASK-SPECIFIC REQUIREMENTS:
{task_requirements}

RUBRIC — STRUCTURE (1–5):
1: {s1}
2: {s2}
3: {s3}
4: {s4}
5: {s5}

RUBRIC — HALLUCINATION SUPPRESSION (1–5, 5=zero hallucination):
1: {h1}
2: {h2}
3: {h3}
4: {h4}
5: {h5}

RUBRIC — COMPLETENESS (1–5):
1: {c1}
2: {c2}
3: {c3}
4: {c4}
5: {c5}

RESPONSE TO SCORE:
{response}

Return ONLY this JSON:
{{
  "structure":     {{"score": <int 1-5>, "reason": "<one sentence citing rubric>", "why_not_higher": "<one sentence>"}},
  "hallucination": {{"score": <int 1-5>, "reason": "<one sentence citing rubric>", "why_not_higher": "<one sentence>"}},
  "completeness":  {{"score": <int 1-5>, "reason": "<one sentence citing rubric>", "why_not_higher": "<one sentence>"}}
}}"""


def _extract_scorable_text(output: str, prompt_key: str = "") -> str:
    """
    Extract the scorable natural language content from agent output.

    - WLM-JSON:   extract s_layer.response
    - WLM-SL:     extract RESP: ... block (multi-line)
    - WLM-HYBRID: extract all fields as structured prose for judge
    - Baselines:  return raw output unchanged
    """
    import re
    stripped = output.strip()

    # ── WLM-HYBRID / WLM-HYBRID-V2: flatten fields into readable prose ────────
    if prompt_key in ("wlm_hybrid", "wlm_hybrid_v2") or (
        stripped.startswith("{") and
        '"definitions"' in stripped and '"final_answer"' in stripped
    ):
        try:
            data = json.loads(stripped)
            # v2 fields (preferred order)
            v2_fields = {
                "definitions":        "DEFINITIONS",
                "structure":          "STRUCTURE",
                "mappings":           "MAPPINGS",
                "examples":           "EXAMPLES",
                "epistemics":         "EPISTEMICS",
                "completeness_check": "COMPLETENESS CHECK",
                "final_answer":       "FINAL ANSWER",
            }
            # v1 fields fallback
            v1_fields = {
                "definitions":    "DEFINITIONS",
                "mappings":       "MAPPINGS",
                "rendering_plan": "RENDERING PLAN",
                "examples":       "EXAMPLES",
                "epistemics":     "EPISTEMICS",
                "constraints":    "CONSTRAINTS",
                "final_answer":   "FINAL ANSWER",
            }
            field_map = v2_fields if "structure" in data else v1_fields
            parts = []
            for field, label in field_map.items():
                val = data.get(field, "")
                if val:
                    parts.append(f"[{label}] {val}")
            if parts:
                return "\n\n".join(parts)
        except Exception:
            pass

    # ── WLM-JSON: extract s_layer.response ───────────────────────────────────
    if stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            resp = data.get("s_layer", {}).get("response", "")
            if resp and len(resp) > 20:
                return resp
        except Exception:
            pass
        match = re.search(
            r'"response"\s*:\s*"(.*?)(?<!\\)"\s*,?\s*"icc_verified"',
            output, re.DOTALL
        )
        if match:
            extracted = match.group(1)
            extracted = extracted.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
            if len(extracted) > 20:
                return extracted

    # ── WLM-SL: extract RESP: ... block ──────────────────────────────────────
    if "RESP:" in output:
        resp_lines, in_resp = [], False
        for line in output.splitlines():
            s = line.strip()
            if s.startswith("RESP:"):
                in_resp = True
                rest = s[5:].strip()
                if rest:
                    resp_lines.append(rest)
                continue
            if in_resp:
                if any(s.startswith(k) for k in ("VERIFY:", "TRACE:", "EPISTEMIC:", "ICC:")):
                    break
                resp_lines.append(line)
        extracted = "\n".join(resp_lines).strip()
        if extracted and len(extracted) > 20:
            return extracted

    return output


def _build_prompt(task: Dict, result: Dict) -> str:
    rb = task.get("rubric", {})
    requirements = "\n".join(f"  • {k}: {v}" for k, v in rb.items()) or "  • Apply general rubric."

    # Extract scorable text — judges must see natural language, not JSON structure
    prompt_key    = result.get("prompt_key", "")
    scorable_text = _extract_scorable_text(result["output"], prompt_key)
    response_text = scorable_text[:4000]
    if len(scorable_text) > 4000:
        response_text += "\n[... truncated ...]"

    s = RUBRIC["structure"]
    h = RUBRIC["hallucination"]
    c = RUBRIC["completeness"]
    return JUDGE_PROMPT.format(
        task_type=task.get("type",""),
        task_input=task["input"][:500],
        task_requirements=requirements,
        s1=s[1],s2=s[2],s3=s[3],s4=s[4],s5=s[5],
        h1=h[1],h2=h[2],h3=h[3],h4=h[4],h5=h[5],
        c1=c[1],c2=c[2],c3=c[3],c4=c[4],c5=c[5],
        response=response_text,
    )


def _parse_judge_response(raw: str) -> Dict:
    try:
        parsed = json.loads(raw.strip())
        return {
            "structure":              int(parsed["structure"]["score"]),
            "hallucination":          int(parsed["hallucination"]["score"]),
            "completeness":           int(parsed["completeness"]["score"]),
            "structure_reason":       parsed["structure"]["reason"],
            "hallucination_reason":   parsed["hallucination"]["reason"],
            "completeness_reason":    parsed["completeness"]["reason"],
            "structure_why_not":      parsed["structure"].get("why_not_higher",""),
            "hallucination_why_not":  parsed["hallucination"].get("why_not_higher",""),
            "completeness_why_not":   parsed["completeness"].get("why_not_higher",""),
            "parse_error":            False,
        }
    except Exception as e:
        return {
            "structure": 0, "hallucination": 0, "completeness": 0,
            "structure_reason": f"PARSE_ERROR: {e}",
            "hallucination_reason": raw[:200],
            "completeness_reason": "",
            "structure_why_not": "",
            "hallucination_why_not": "",
            "completeness_why_not": "",
            "parse_error": True,
        }


def _token_efficiency(scores: Dict, output_tokens: int) -> float:
    mu = (scores["structure"] + scores["hallucination"] + scores["completeness"]) / 3.0
    return round(mu / math.log(output_tokens + 1), 4) if output_tokens > 0 else 0.0


def score_output(task: Dict, result: Dict) -> Dict[str, Any]:
    """
    Score using both Claude and GPT-4o judges.
    Returns scores from each judge + agreement metrics.
    """
    prompt   = _build_prompt(task, result)
    output_tokens = result.get("output_tokens", 1)
    all_scores = {}

    for judge_key in JUDGES:
        try:
            resp = call_model(
                model_key  = judge_key,
                system     = JUDGE_SYSTEM,
                user_input = prompt,
                registry   = JUDGES,
            )
            parsed = _parse_judge_response(resp["output"])
        except Exception as e:
            parsed = {
                "structure": 0, "hallucination": 0, "completeness": 0,
                "structure_reason": f"JUDGE_ERROR: {e}",
                "hallucination_reason": "", "completeness_reason": "",
                "structure_why_not": "", "hallucination_why_not": "",
                "completeness_why_not": "", "parse_error": True,
            }
        parsed["token_efficiency"] = _token_efficiency(parsed, output_tokens)
        all_scores[judge_key] = parsed

    # ── Inter-judge agreement ─────────────────────────────────────────────────
    dims = ["structure", "hallucination", "completeness"]
    agreement = {}
    if len(all_scores) == 2:
        j1, j2 = list(all_scores.values())
        for d in dims:
            diff = abs(float(j1[d]) - float(j2[d]))
            agreement[f"{d}_diff"] = round(diff, 3)
        agreement["exact_match"] = all(agreement[f"{d}_diff"] == 0.0 for d in dims)
        agreement["mean_diff"]   = round(
            sum(agreement[f"{d}_diff"] for d in dims) / 3, 3
        )

        # Consensus: mean of both judges
        consensus = {}
        for d in dims:
            consensus[d] = round((float(j1[d]) + float(j2[d])) / 2, 2)
        consensus["token_efficiency"] = round(
            (float(j1["token_efficiency"]) + float(j2["token_efficiency"])) / 2, 4
        )
    else:
        # Fallback: use whichever judge ran
        j = list(all_scores.values())[0]
        consensus = {k: float(v) if isinstance(v, (int, float)) else v
                     for k, v in j.items()}
        agreement = {"mean_diff": 0.0, "exact_match": True}

    return {
        "scores_by_judge": all_scores,
        "consensus":       consensus,
        "agreement":       agreement,
    }
