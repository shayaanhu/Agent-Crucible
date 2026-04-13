from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


def main() -> None:
    if load_dotenv is not None:
        load_dotenv()
    parser = argparse.ArgumentParser(description="Run red-team dataset through orchestrator.")
    parser.add_argument(
        "--dataset",
        default="eval/fixtures/red_team_objectives.json",
        help="Path to dataset JSON file.",
    )
    parser.add_argument("--provider", default="groq", help="Target provider.")
    parser.add_argument("--attacker-provider", default="", help="Attacker provider override.")
    parser.add_argument("--max-turns", type=int, default=3, help="Max turns per objective.")
    parser.add_argument("--limit", type=int, default=0, help="Optional cap on the number of objectives to run.")
    parser.add_argument("--category", default="", help="Run only objectives in this category.")
    parser.add_argument("--difficulty", default="", help="Run only objectives in this difficulty tier.")
    parser.add_argument("--strategy", default="", help="Run only objectives for this strategy.")
    parser.add_argument(
        "--cooldown-seconds",
        type=float,
        default=10.0,
        help="Seconds to wait between dataset objectives to reduce provider rate limits.",
    )
    args = parser.parse_args()

    from agents.red.red_team import get_red_team_agent, trace_to_dict
    from eval.red_team_eval_utils import summarize_red_team_results, timestamp_fields

    dataset_path = Path(args.dataset)
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(dataset_payload, dict):
        suite_metadata = dataset_payload.get("suite_metadata", {})
        objectives = list(dataset_payload.get("cases", []))
    else:
        suite_metadata = {}
        objectives = list(dataset_payload)

    if args.category:
        objectives = [obj for obj in objectives if obj.get("category", "") == args.category]
    if args.difficulty:
        objectives = [obj for obj in objectives if obj.get("difficulty", "") == args.difficulty]
    if args.strategy:
        objectives = [obj for obj in objectives if obj.get("strategy_id", "") == args.strategy]
    if args.limit > 0:
        objectives = objectives[: args.limit]

    agent = get_red_team_agent()
    results: list[dict] = []
    total_objectives = len(objectives)
    progress = tqdm(
        total=total_objectives,
        desc="red-team dataset",
        unit="objective",
        dynamic_ncols=True,
    )

    for index, obj in enumerate(objectives, start=1):
        metadata = {
            "strategy_id": obj.get("strategy_id", "direct_jailbreak"),
            "objective_goal": obj.get("goal", ""),
            "objective_success_tokens": obj.get("objective_success_tokens", ""),
            "objective_block_tokens": obj.get("objective_block_tokens", ""),
            "objective_tags": obj.get("objective_tags", ""),
            "objective_category": obj.get("category", ""),
            "objective_difficulty": obj.get("difficulty", ""),
            "dataset_id": obj.get("id", "unknown"),
        }
        if args.attacker_provider:
            metadata["attacker_provider"] = args.attacker_provider
        progress.set_postfix_str(f"{obj.get('id', 'unknown')}:{metadata['strategy_id']}")
        trace = agent.run_attack(
            scenario=obj.get("scenario", ""),
            goal=obj.get("goal", ""),
            max_turns=args.max_turns,
            provider=args.provider,
            metadata=metadata,
        )
        results.append(trace_to_dict(trace))
        progress.update(1)
        if index < total_objectives:
            progress.set_postfix_str(
                f"{obj.get('id', 'unknown')}:{metadata['strategy_id']} cooldown={args.cooldown_seconds:.0f}s"
            )
            time.sleep(args.cooldown_seconds)

    progress.close()

    payload = {
        "run_metadata": {
            "suite_type": "objective_suite",
            "runner": "red_team_dataset",
            **timestamp_fields(),
            "provider": args.provider,
            "attacker_provider": args.attacker_provider or args.provider,
            "max_turns": args.max_turns,
            "cooldown_seconds": args.cooldown_seconds,
            "dataset_path": str(dataset_path),
            "suite_name": suite_metadata.get("suite_name", ""),
            "suite_version": suite_metadata.get("suite_version", ""),
            "category_filter": args.category,
            "difficulty_filter": args.difficulty,
            "strategy_filter": args.strategy,
            "limit": args.limit,
            "total_objectives": total_objectives,
            "total_results": len(results),
        },
        "summary": summarize_red_team_results(results),
        "results": results,
    }

    out_path = output_dir / "red_team_dataset_results.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} dataset traces to {out_path}", flush=True)


if __name__ == "__main__":
    main()
