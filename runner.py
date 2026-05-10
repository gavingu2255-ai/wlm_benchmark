#!/usr/bin/env python3
# runner.py  —  WLM Benchmark main runner
# Usage:
#   python runner.py                                          # all models, all prompts, all tasks
#   python runner.py --models claude,gpt-4o --prompts wlm_json,base_a
#   python runner.py --models qwen-7b,gemma-4b --tasks T04,T05
#   python runner.py --models all --prompts wlm_sl --dry-run

import argparse
import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from config        import MODELS, PROMPTS, DEFAULT_TASKS, RESULTS_DIR
from tasks.benchmark import TASKS, TASK_MAP
from prompts        import get_prompt
from models.caller  import call_model
from scoring.judge  import score_output


# ── Output helpers ────────────────────────────────────────────────────────────

CSV_FIELDS = [
    "task_id", "task_type", "model_key", "model_id", "prompt_key",
    # Claude judge (primary)
    "claude_structure", "claude_hallucination", "claude_completeness",
    "claude_token_efficiency", "claude_parse_error",
    # GPT-4o judge (validation)
    "gpt4o_structure", "gpt4o_hallucination", "gpt4o_completeness",
    "gpt4o_token_efficiency", "gpt4o_parse_error",
    # Inter-judge agreement
    "agreement_structure_diff", "agreement_hallucination_diff",
    "agreement_completeness_diff", "agreement_mean_diff", "agreement_exact_match",
    # Metadata
    "output_tokens", "total_tokens", "latency_s", "api",
]


def _flatten_scores(result: Dict, scores: Dict) -> Dict:
    """Flatten nested score structure into CSV-ready dict.
    Both judges stored independently. No consensus averaging.
    parse_error=True rows should be excluded from analysis.
    """
    row = {
        "task_id":       result["task_id"],
        "task_type":     result["task_type"],
        "model_key":     result["model_key"],
        "model_id":      result["model_id"],
        "prompt_key":    result["prompt_key"],
        "output_tokens": result.get("output_tokens", 0),
        "total_tokens":  result.get("total_tokens", 0),
        "latency_s":     result.get("latency_s", 0),
        "api":           result.get("api", ""),
    }
    # Per-judge scores — stored independently, not averaged
    for judge_key in ["claude", "gpt4o"]:
        js = scores["scores_by_judge"].get(judge_key, {})
        for dim in ["structure", "hallucination", "completeness", "token_efficiency"]:
            row[f"{judge_key}_{dim}"] = js.get(dim, 0)
        row[f"{judge_key}_parse_error"] = js.get("parse_error", True)

    # Agreement metrics
    ag = scores.get("agreement", {})
    for k in ["structure_diff","hallucination_diff","completeness_diff",
              "mean_diff","exact_match"]:
        row[f"agreement_{k}"] = ag.get(k, "")

    return row


# ── Core runner ───────────────────────────────────────────────────────────────

def run_experiment(
    model_keys:  List[str],
    prompt_keys: List[str],
    task_ids:    List[str],
    dry_run:     bool = False,
    output_tag:  str  = "",
) -> None:

    tag      = output_tag or f"run_{int(time.time())}"
    jsonl_path = RESULTS_DIR / f"{tag}_outputs.jsonl"
    csv_path   = RESULTS_DIR / f"{tag}_scores.csv"

    combos = [(m, p, t) for m in model_keys for p in prompt_keys for t in task_ids]
    total  = len(combos)

    print(f"\nWLM Benchmark")
    print(f"  Models : {model_keys}")
    print(f"  Prompts: {prompt_keys}")
    print(f"  Tasks  : {task_ids}")
    print(f"  Total  : {total} runs  (× 2 judges = {total*2} scoring calls)")
    print(f"  Output : {tag}")
    if dry_run:
        print(f"\n  DRY RUN — no API calls made.")
        return
    print()

    jsonl_fh = jsonl_path.open("w", encoding="utf-8")
    csv_fh   = csv_path.open("w", encoding="utf-8", newline="")
    csv_writer = csv.DictWriter(csv_fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
    csv_writer.writeheader()

    n = 0
    for model_key, prompt_key, task_id in combos:
        n += 1
        task   = TASK_MAP[task_id]
        prompt = get_prompt(
            prompt_key,
            task_injection   = task.get("prompt_injection", ""),
            hybrid_injection = task.get("hybrid_injection", ""),
        )
        label  = f"{model_key}/{prompt_key}/{task_id}"

        print(f"  [{n:03d}/{total}] {label:<45}", end=" ", flush=True)

        # ── Agent call ────────────────────────────────────────────────────────
        agent_result = call_model(
            model_key  = model_key,
            system     = prompt,
            user_input = task["input"],
        )
        agent_result["task_id"]   = task_id
        agent_result["task_type"] = task["type"]
        agent_result["prompt_key"] = prompt_key

        if "error" in agent_result:
            print(f"✗  AGENT ERROR: {agent_result['error'][:50]}")
            jsonl_fh.write(json.dumps(agent_result, ensure_ascii=False) + "\n")
            continue

        tok = agent_result["output_tokens"]
        print(f"tok={tok:4d}  → judging...", end=" ", flush=True)

        # ── Judge calls ───────────────────────────────────────────────────────
        try:
            scores = score_output(task, agent_result)
            ag     = scores.get("agreement", {})
            cons   = scores.get("consensus", {})
            cj   = scores.get("scores_by_judge",{}).get("claude",{})
            gj   = scores.get("scores_by_judge",{}).get("gpt4o",{})
            ag   = scores.get("agreement",{})
            c_ok = not cj.get("parse_error", True)
            g_ok = not gj.get("parse_error", True)
            print(
                f"✓  "
                f"C:s={cj.get('structure',0):.0f} h={cj.get('hallucination',0):.0f} "
                f"c={cj.get('completeness',0):.0f} η={cj.get('token_efficiency',0):.3f}"
                f"{'✓' if c_ok else '✗'}  "
                f"G:s={gj.get('structure',0):.0f} h={gj.get('hallucination',0):.0f} "
                f"c={gj.get('completeness',0):.0f}"
                f"{'✓' if g_ok else '✗'}  "
                f"Δ={ag.get('mean_diff','?')}"
            )
        except Exception as e:
            print(f"✗  JUDGE ERROR: {e}")
            scores = {"scores_by_judge":{}, "consensus":{}, "agreement":{}}

        # ── Save ──────────────────────────────────────────────────────────────
        try:
            full = {**agent_result, "scores": scores}
            jsonl_fh.write(json.dumps(full, ensure_ascii=False) + "\n")
            row = _flatten_scores(agent_result, scores)
            csv_writer.writerow(row)
        except Exception as e:
            print(f"  ✗  SAVE ERROR [{label}]: {e}")
            # Write minimal error record so we don't lose the row
            try:
                err_row = {k: "" for k in CSV_FIELDS}
                err_row.update({
                    "task_id": task_id, "task_type": task["type"],
                    "model_key": model_key, "prompt_key": prompt_key,
                })
                csv_writer.writerow(err_row)
            except Exception:
                pass

        # Flush after each row so partial results are safe
        jsonl_fh.flush()
        csv_fh.flush()

        time.sleep(0.5)

    jsonl_fh.close()
    csv_fh.close()
    print(f"\n  Outputs → {jsonl_path}")
    print(f"  Scores  → {csv_path}")
    print(f"\nDone. Run  python analyze.py --tag {tag}  to generate figures.")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_list(val: str, valid: List[str], name: str) -> List[str]:
    if val == "all":
        return valid
    keys = [v.strip() for v in val.split(",")]
    for k in keys:
        if k not in valid:
            raise ValueError(f"Unknown {name}: '{k}'. Valid: {valid}")
    return keys


def main():
    parser = argparse.ArgumentParser(description="WLM Benchmark Runner")
    parser.add_argument("--models",  default="all", help="comma-separated model keys or 'all'")
    parser.add_argument("--prompts", default="all", help="comma-separated prompt keys or 'all'")
    parser.add_argument("--tasks",   default="all", help="comma-separated task IDs or 'all'")
    parser.add_argument("--tag",     default="",    help="output filename tag (default: timestamp)")
    parser.add_argument("--dry-run", action="store_true", help="print plan without making API calls")
    args = parser.parse_args()

    model_keys  = parse_list(args.models,  list(MODELS.keys()),  "model")
    prompt_keys = parse_list(args.prompts, list(PROMPTS.keys()), "prompt")
    task_ids    = parse_list(args.tasks,   DEFAULT_TASKS,        "task")

    run_experiment(
        model_keys  = model_keys,
        prompt_keys = prompt_keys,
        task_ids    = task_ids,
        dry_run     = args.dry_run,
        output_tag  = args.tag,
    )


if __name__ == "__main__":
    main()
