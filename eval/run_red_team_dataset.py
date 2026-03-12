from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    parser.add_argument("--provider", default="mock", help="Target provider.")
    parser.add_argument("--attacker-provider", default="", help="Attacker provider override.")
    parser.add_argument("--max-turns", type=int, default=3, help="Max turns per objective.")
    args = parser.parse_args()

    from agents.red_team import get_red_team_agent, trace_to_dict

    dataset_path = Path(args.dataset)
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    objectives = json.loads(dataset_path.read_text(encoding="utf-8"))
    agent = get_red_team_agent()
    results: list[dict] = []

    for obj in objectives:
        metadata = {
            "strategy_id": obj.get("strategy_id", "direct_jailbreak"),
            "objective_goal": obj.get("goal", ""),
            "objective_success_tokens": obj.get("objective_success_tokens", ""),
            "objective_block_tokens": obj.get("objective_block_tokens", ""),
            "objective_tags": obj.get("objective_tags", ""),
            "dataset_id": obj.get("id", "unknown"),
        }
        if args.attacker_provider:
            metadata["attacker_provider"] = args.attacker_provider
        trace = agent.run_attack(
            scenario=obj.get("scenario", ""),
            goal=obj.get("goal", ""),
            max_turns=args.max_turns,
            provider=args.provider,
            metadata=metadata,
        )
        results.append(trace_to_dict(trace))

    out_path = output_dir / "red_team_dataset_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} dataset traces to {out_path}")


if __name__ == "__main__":
    main()
