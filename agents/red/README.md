# agents/red/

Red-team agent that generates adversarial multi-turn attacks against a target model.

---

## Files

| File | Description |
|------|-------------|
| `red_team.py` | Top-level red-team agent — entry point called by the pipeline |
| `red_team_runtime.py` | Conversation loop — drives turns, collects responses |
| `red_team_strategies.py` | All attack strategy implementations and the strategy registry |
| `red_team_models.py` | Pydantic models for attack configs and turn records |
| `red_team_objective.py` | Objective-driven attack mode (used by the eval suite) |
| `red_team_scorers.py` | Scoring logic — determines if an attack succeeded |
| `red_team_converters.py` | Converts internal records to evaluation-ready formats |
| `target_runtime.py` | Wraps the target model so the red-team agent can call it |

---

## How an attack works

1. The pipeline calls `red_team.py` with a scenario, goal, strategy ID, and provider.
2. The strategy generates an opening prompt.
3. `red_team_runtime.py` sends the prompt to the target model via `target_runtime.py`.
4. The target model's response is passed to the blue-team pipeline for a verdict.
5. Based on the verdict and conversation history the strategy generates the next prompt.
6. This repeats for `max_turns` or until the attack objective is met.
