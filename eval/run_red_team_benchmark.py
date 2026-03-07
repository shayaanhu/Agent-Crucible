from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
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
            trace = agent.run_attack(
                scenario=fixture["scenario"],
                goal=fixture["goal"],
                max_turns=3,
                provider="mock",
                metadata={"strategy_id": strategy_id, "fixture_id": fixture["id"]},
            )
            results.append(trace_to_dict(trace))

    out_path = output_dir / "red_team_benchmark_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} benchmark traces to {out_path}")


if __name__ == "__main__":
    main()
