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
    parser = argparse.ArgumentParser(description="Run red-team benchmark fixtures.")
    parser.add_argument("--provider", default="groq", help="Target provider.")
    parser.add_argument("--attacker-provider", default="", help="Attacker provider override.")
    parser.add_argument("--max-turns", type=int, default=3, help="Max turns per fixture.")
    args = parser.parse_args()

    from agents.red_team import get_red_team_agent, trace_to_dict

    fixtures_dir = Path("eval/fixtures/red_team")
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    agent = get_red_team_agent()
    results: list[dict] = []

    for fixture_file in sorted(fixtures_dir.glob("*.json")):
        strategy_id = fixture_file.stem
        with fixture_file.open("r", encoding="utf-8") as f:
            fixtures = json.load(f)
        for fixture in fixtures:
            metadata = {"strategy_id": strategy_id, "fixture_id": fixture["id"]}
            if args.attacker_provider:
                metadata["attacker_provider"] = args.attacker_provider
            trace = agent.run_attack(
                scenario=fixture["scenario"],
                goal=fixture["goal"],
                max_turns=args.max_turns,
                provider=args.provider,
                metadata=metadata,
            )
            results.append(trace_to_dict(trace))

    out_path = output_dir / "red_team_benchmark_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} benchmark traces to {out_path}")


if __name__ == "__main__":
    main()
