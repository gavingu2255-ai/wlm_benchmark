#!/usr/bin/env python3
"""
run_exp2.py  —  Experiment 2 runner
T08–T37, domain-independent tasks
Large models (claude, gpt-4o): wlm_sl + wlm_json + base_a + base_b
Small models (gpt-4o-mini, qwen-7b, gemma-4b): wlm_sl + base_a + base_b

Usage:
    python run_exp2.py                        # full Exp2 (510 runs)
    python run_exp2.py --tier large           # large models only (240 runs)
    python run_exp2.py --tier small           # small models only (270 runs)
    python run_exp2.py --dry-run              # plan without API calls
    python run_exp2.py --tasks T08,T09,T10   # specific tasks only
    python run_exp2.py --resume               # skip already-completed rows
"""

import argparse, csv, json, time
from pathlib import Path

from config import (
    MODELS, RESULTS_DIR,
    EXP2_TASKS, EXP2_LARGE_MODELS, EXP2_SMALL_MODELS,
    EXP2_LARGE_PROMPTS, EXP2_SMALL_PROMPTS,
)
from tasks.benchmark import TASK_MAP
from prompts         import get_prompt
from models.caller   import call_model
from scoring.judge   import score_output

CSV_FIELDS = [
    "run_id", "task_id", "task_type", "model_key", "model_id", "prompt_key",
    "claude_structure", "claude_hallucination", "claude_completeness",
    "claude_token_efficiency", "claude_parse_error",
    "gpt4o_structure", "gpt4o_hallucination", "gpt4o_completeness",
    "gpt4o_token_efficiency", "gpt4o_parse_error",
    "agreement_structure_diff", "agreement_hallucination_diff",
    "agreement_completeness_diff", "agreement_mean_diff", "agreement_exact_match",
    "output_tokens", "total_tokens", "latency_s", "api", "temperature",
    "experiment",
]


def load_completed(csv_path):
    """Return set of (model_key, prompt_key, task_id) already in the CSV."""
    done = set()
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add((row["model_key"], row["prompt_key"], row["task_id"]))
    return done


def flatten(result, scores, temperature):
    row = {
        "run_id":        1,
        "experiment":    "exp2",
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


def run_exp2(tier="all", task_filter=None, dry_run=False,
             tag="exp2", temperature=0.7, resume=False):

    # Build combos
    combos = []
    tasks = task_filter or EXP2_TASKS

    if tier in ("all", "large"):
        for m in EXP2_LARGE_MODELS:
            for p in EXP2_LARGE_PROMPTS:
                for t in tasks:
                    combos.append((m, p, t))

    if tier in ("all", "small"):
        for m in EXP2_SMALL_MODELS:
            for p in EXP2_SMALL_PROMPTS:
                for t in tasks:
                    combos.append((m, p, t))

    jsonl_path = RESULTS_DIR / f"{tag}_outputs.jsonl"
    csv_path   = RESULTS_DIR / f"{tag}_scores.csv"

    # Resume: skip completed
    completed = load_completed(csv_path) if resume else set()
    if resume and completed:
        before = len(combos)
        combos = [(m, p, t) for m, p, t in combos if (m, p, t) not in completed]
        print(f"  Resume: skipping {before - len(combos)} completed rows")

    total = len(combos)
    large_runs = sum(1 for m, p, t in combos if m in EXP2_LARGE_MODELS)
    small_runs = total - large_runs

    print(f"\nWLM Benchmark — Experiment 2")
    print(f"  Tier       : {tier}")
    print(f"  Tasks      : {tasks}")
    print(f"  Large runs : {large_runs}  (× 2 judges = {large_runs*2} scoring calls)")
    print(f"  Small runs : {small_runs}  (× 2 judges = {small_runs*2} scoring calls)")
    print(f"  Total      : {total} runs  (× 2 judges = {total*2} scoring calls)")
    print(f"  Output     : {tag}")
    print(f"  Resume     : {resume}")

    if dry_run:
        print("\n  DRY RUN — no API calls.\n")
        # Show plan breakdown
        from collections import Counter
        model_counts  = Counter(m for m, p, t in combos)
        prompt_counts = Counter(p for m, p, t in combos)
        print("  Model breakdown:")
        for m, n in sorted(model_counts.items()):
            print(f"    {m:20s}: {n} runs")
        print("  Prompt breakdown:")
        for p, n in sorted(prompt_counts.items()):
            print(f"    {p:20s}: {n} runs")
        return

    # Open files
    file_exists = csv_path.exists()
    jsonl_fh = jsonl_path.open("a", encoding="utf-8")
    csv_fh   = csv_path.open("a", encoding="utf-8", newline="")
    writer   = csv.DictWriter(csv_fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
    if not file_exists:
        writer.writeheader()

    n = 0
    errors = 0
    t_start = time.time()

    for model_key, prompt_key, task_id in combos:
        n += 1
        task   = TASK_MAP[task_id]
        prompt = get_prompt(
            prompt_key,
            task_injection   = task.get("prompt_injection", ""),
            hybrid_injection = task.get("hybrid_injection", ""),
        )
        label  = f"{model_key}/{prompt_key}/{task_id}"
        elapsed_total = time.time() - t_start
        eta = (elapsed_total / n) * (total - n) if n > 1 else 0
        print(f"  [{n:03d}/{total}] {label:<48} ETA:{eta/60:.0f}m", end=" ", flush=True)

        result = call_model(
            model_key   = model_key,
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
            jsonl_fh.write(json.dumps({**result, "experiment": "exp2"}, ensure_ascii=False) + "\n")
            continue

        print(f"tok={result['output_tokens']:4d} → judging...", end=" ", flush=True)

        try:
            scores = score_output(task, result)
            cj = scores.get("scores_by_judge", {}).get("claude", {})
            gj = scores.get("scores_by_judge", {}).get("gpt4o", {})
            ag = scores.get("agreement", {})
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
            jsonl_fh.write(json.dumps({**result, "scores": scores, "experiment": "exp2"},
                           ensure_ascii=False) + "\n")
            writer.writerow(flatten(result, scores, temperature))
        except Exception as e:
            print(f"  ✗ SAVE: {e}")

        jsonl_fh.flush()
        csv_fh.flush()
        time.sleep(0.3)

    jsonl_fh.close()
    csv_fh.close()

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  Done in {elapsed/60:.1f} min  |  {n} runs  |  {errors} errors")
    print(f"  Outputs → {jsonl_path}")
    print(f"  Scores  → {csv_path}")
    print(f"\n  Next: python analyze_exp2.py --tag {tag}")


def main():
    parser = argparse.ArgumentParser(description="WLM Exp2 Runner (T08-T37)")
    parser.add_argument("--tier",        default="all",
                        choices=["all", "large", "small"],
                        help="which model tier to run")
    parser.add_argument("--tasks",       default="",
                        help="comma-separated task IDs (default: all T08-T37)")
    parser.add_argument("--tag",         default="exp2",
                        help="output file tag")
    parser.add_argument("--temperature", default=0.7, type=float)
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--resume",      action="store_true",
                        help="skip already-completed rows")
    args = parser.parse_args()

    task_filter = None
    if args.tasks:
        task_filter = [t.strip() for t in args.tasks.split(",")]
        for t in task_filter:
            if t not in TASK_MAP:
                raise ValueError(f"Unknown task: {t}")

    run_exp2(
        tier        = args.tier,
        task_filter = task_filter,
        dry_run     = args.dry_run,
        tag         = args.tag,
        temperature = args.temperature,
        resume      = args.resume,
    )


if __name__ == "__main__":
    main()