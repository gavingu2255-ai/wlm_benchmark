#!/usr/bin/env python3
"""
run_gemini.py  —  Gemini 1.5 Pro: Exp1 + Exp2 + Exp3 combined runner
Judge: Claude + GPT-4o (same as all other experiments)

Exp1: 5 formats × 7 tasks  =  35 runs
Exp2: 5 formats × 30 tasks = 150 runs
Exp3: 3 formats × 8 tasks  =  24 runs
Total: 209 runs × 2 judges = 418 judge calls

Usage:
    python run_gemini.py                    # all three experiments
    python run_gemini.py --exp 1            # Exp1 only
    python run_gemini.py --exp 2            # Exp2 only
    python run_gemini.py --exp 3            # Exp3 only
    python run_gemini.py --exp 1,2          # Exp1 and Exp2
    python run_gemini.py --dry-run
    python run_gemini.py --resume
"""

import argparse, csv, json, time
from pathlib import Path

from config import (
    MODELS, RESULTS_DIR,
    DEFAULT_TASKS,
    EXP1_LARGE_PROMPTS,
    EXP2_LARGE_PROMPTS,
    EXP3_TASKS_IDS, EXP3_LARGE_PROMPTS,
)
from tasks.benchmark import TASK_MAP, EXP2_TASK_IDS as EXP2_TASKS
from prompts         import get_prompt
from models.caller   import call_model
from scoring.judge   import score_output

MODEL_KEY = "gemini-pro"

CSV_FIELDS = [
    "run_id", "experiment", "task_id", "task_type",
    "model_key", "model_id", "prompt_key",
    "claude_structure", "claude_hallucination", "claude_completeness",
    "claude_token_efficiency", "claude_parse_error",
    "gpt4o_structure", "gpt4o_hallucination", "gpt4o_completeness",
    "gpt4o_token_efficiency", "gpt4o_parse_error",
    "agreement_structure_diff", "agreement_hallucination_diff",
    "agreement_completeness_diff", "agreement_mean_diff", "agreement_exact_match",
    "output_tokens", "total_tokens", "latency_s", "api", "temperature",
]

EXP_CONFIGS = {
    1: {
        "tasks":   DEFAULT_TASKS,
        "prompts": EXP1_LARGE_PROMPTS,
        "label":   "Exp1 (T01-T07, 7 tasks)",
    },
    2: {
        "tasks":   EXP2_TASKS,
        "prompts": EXP2_LARGE_PROMPTS,
        "label":   "Exp2 (T08-T37, 30 tasks)",
    },
    3: {
        "tasks":   EXP3_TASKS_IDS,
        "prompts": ["wlm_hybrid_v2","wlm_sl","wlm_json","base_a","base_b"],  # All 5 for Gemini validation
        "label":   "Exp3 (T38-T52 stress test, 8 tasks, 5 formats for Gemini)",
    },
}


def load_completed(csv_path):
    done = set()
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add((row["experiment"], row["prompt_key"], row["task_id"]))
    return done


def flatten(result, scores, experiment, temperature):
    row = {
        "run_id":        1,
        "experiment":    f"exp{experiment}",
        "task_id":       result["task_id"],
        "task_type":     result["task_type"],
        "model_key":     result["model_key"],
        "model_id":      result["model_id"],
        "prompt_key":    result["prompt_key"],
        "output_tokens": result.get("output_tokens", 0),
        "total_tokens":  result.get("total_tokens", 0),
        "latency_s":     result.get("latency_s", 0),
        "api":           result.get("api", ""),
        "temperature":   temperature,
    }
    for judge in ["claude", "gpt4o"]:
        js = scores["scores_by_judge"].get(judge, {})
        for dim in ["structure", "hallucination", "completeness", "token_efficiency"]:
            row[f"{judge}_{dim}"] = js.get(dim, 0)
        row[f"{judge}_parse_error"] = js.get("parse_error", True)
    ag = scores.get("agreement", {})
    for k in ["structure_diff", "hallucination_diff", "completeness_diff",
              "mean_diff", "exact_match"]:
        row[f"agreement_{k}"] = ag.get(k, "")
    return row


def run_gemini(exps, dry_run=False, tag="gemini_all",
               temperature=0.7, resume=False):

    # Build combo list: (exp_num, prompt_key, task_id)
    combos = []
    for exp in exps:
        cfg = EXP_CONFIGS[exp]
        for p in cfg["prompts"]:
            for t in cfg["tasks"]:
                combos.append((exp, p, t))

    jsonl_path = RESULTS_DIR / f"{tag}_outputs.jsonl"
    csv_path   = RESULTS_DIR / f"{tag}_scores.csv"

    completed = load_completed(csv_path) if resume else set()
    if resume and completed:
        before = len(combos)
        combos = [(e, p, t) for e, p, t in combos
                  if (f"exp{e}", p, t) not in completed]
        print(f"  Resume: skipping {before - len(combos)} completed rows")

    total = len(combos)

    print(f"\nWLM Benchmark — Gemini 1.5 Pro")
    print(f"  Model      : {MODEL_KEY} (gemini-1.5-pro)")
    print(f"  Judge      : Claude + GPT-4o (unchanged)")
    print(f"  Experiments: {exps}")
    for exp in exps:
        cfg    = EXP_CONFIGS[exp]
        n_runs = len(cfg["prompts"]) * len(cfg["tasks"])
        print(f"    {cfg['label']}: {len(cfg['prompts'])} formats × "
              f"{len(cfg['tasks'])} tasks = {n_runs} runs")
    print(f"  Total      : {total} runs × 2 judges = {total*2} judge calls")
    print(f"  Output     : {tag}")

    if dry_run:
        print("\n  DRY RUN — no API calls.\n")
        from collections import Counter
        print("  Prompt breakdown:")
        for p, n in sorted(Counter(p for e,p,t in combos).items()):
            print(f"    {p:20s}: {n}")
        print("  Experiment breakdown:")
        for e, n in sorted(Counter(e for e,p,t in combos).items()):
            print(f"    Exp{e}: {n}")
        return

    file_exists = csv_path.exists()
    jsonl_fh = jsonl_path.open("a", encoding="utf-8")
    csv_fh   = csv_path.open("a", encoding="utf-8", newline="")
    writer   = csv.DictWriter(csv_fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
    if not file_exists:
        writer.writeheader()

    n = 0
    errors = 0
    t_start = time.time()

    for exp, prompt_key, task_id in combos:
        n += 1
        task   = TASK_MAP[task_id]
        prompt = get_prompt(
            prompt_key,
            task_injection   = task.get("prompt_injection", ""),
            hybrid_injection = task.get("hybrid_injection", ""),
        )
        label   = f"exp{exp}/{prompt_key}/{task_id}"
        elapsed = time.time() - t_start
        eta     = (elapsed / n) * (total - n) if n > 1 else 0
        print(f"  [{n:03d}/{total}] {label:<50} ETA:{eta/60:.0f}m",
              end=" ", flush=True)

        result = call_model(
            model_key   = MODEL_KEY,
            system      = prompt,
            user_input  = task["input"],
            temperature = temperature,
        )
        result["task_id"]    = task_id
        result["task_type"]  = task["type"]
        result["prompt_key"] = prompt_key

        if "error" in result:
            print(f"✗ AGENT: {result['error'][:60]}")
            errors += 1
            jsonl_fh.write(json.dumps(
                {**result, "experiment": f"exp{exp}"},
                ensure_ascii=False) + "\n")
            continue

        print(f"tok={result['output_tokens']:4d} → judging...",
              end=" ", flush=True)

        try:
            scores = score_output(task, result)
            cj   = scores.get("scores_by_judge", {}).get("claude", {})
            gj   = scores.get("scores_by_judge", {}).get("gpt4o", {})
            ag   = scores.get("agreement", {})
            c_ok = not cj.get("parse_error", True)
            g_ok = not gj.get("parse_error", True)
            print(
                f"✓ "
                f"C:s={cj.get('structure',0):.0f} h={cj.get('hallucination',0):.0f} "
                f"c={cj.get('completeness',0):.0f} η={cj.get('token_efficiency',0):.3f}"
                f"{'✓' if c_ok else '✗'}  "
                f"G:s={gj.get('structure',0):.0f} h={gj.get('hallucination',0):.0f} "
                f"c={gj.get('completeness',0):.0f}{'✓' if g_ok else '✗'}  "
                f"Δ={ag.get('mean_diff','?')}"
            )
        except Exception as e:
            print(f"✗ JUDGE: {e}")
            scores = {"scores_by_judge": {}, "agreement": {}}
            errors += 1

        try:
            jsonl_fh.write(json.dumps(
                {**result, "scores": scores, "experiment": f"exp{exp}"},
                ensure_ascii=False) + "\n")
            writer.writerow(flatten(result, scores, exp, temperature))
        except Exception as e:
            print(f"  ✗ SAVE: {e}")

        jsonl_fh.flush()
        csv_fh.flush()
        time.sleep(0.5)  # Gemini rate limit buffer

    jsonl_fh.close()
    csv_fh.close()

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  Done in {elapsed/60:.1f} min  |  {n} runs  |  {errors} errors")
    print(f"  Outputs → {jsonl_path}")
    print(f"  Scores  → {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Gemini 1.5 Pro — WLM Benchmark Exp1+2+3")
    parser.add_argument("--exp",         default="1,2,3",
                        help="experiments to run: 1,2,3 or any combination")
    parser.add_argument("--tag",         default="gemini_all")
    parser.add_argument("--temperature", default=0.7, type=float)
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--resume",      action="store_true")
    args = parser.parse_args()

    exps = [int(e.strip()) for e in args.exp.split(",")]
    for e in exps:
        if e not in EXP_CONFIGS:
            raise ValueError(f"Unknown experiment: {e}. Valid: 1, 2, 3")

    run_gemini(
        exps        = exps,
        dry_run     = args.dry_run,
        tag         = args.tag,
        temperature = args.temperature,
        resume      = args.resume,
    )


if __name__ == "__main__":
    main()
