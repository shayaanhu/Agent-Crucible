# Agents

Contains:
1. Red-team attack strategy modules
2. Blue-team guardrail evaluation modules
3. Provider adapter interfaces

Current modules:
1. `red_team.py`
2. `blue_team.py`
3. `blue_team_policies.py`
4. `provider_adapter.py`
5. `mock_provider.py`
6. `contracts.py`
7. `red_team_models.py`
8. `red_team_strategies.py`
9. `red_team_runtime.py`

Parallel ownership model:
1. Red-team: owns `red_team.py`
2. Blue-team: owns `blue_team.py`
3. Shared interface file: `contracts.py` (coordinate before edits)

Red-team strategy IDs:
1. `direct_jailbreak`
2. `roleplay_jailbreak`
3. `policy_confusion`
4. `instruction_override_chain`
5. `context_poisoning`
6. `benign_malicious_sandwich`
7. `system_prompt_probing`
8. `multi_step_escalation`

How to add a new red-team strategy:
1. Implement strategy in `red_team_strategies.py`.
2. Add it to `build_strategy_registry()`.
3. Add fixture file in `eval/fixtures/red_team/<strategy_id>.json`.
4. Add/extend tests in `backend/tests/test_red_team_engine.py`.

How to add a new blue-team policy:
1. Add policy entry in `config/policies.json`.
2. Reload or restart the backend so `blue_team_policies.py` picks up the updated config.
3. Add or extend tests in `backend/tests/test_blue_team_policy_engine.py`.
