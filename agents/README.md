# Agents

Contains:
1. Red-team attack strategy modules
2. Blue-team guardrail evaluation modules
3. Provider adapter interfaces

Current modules:
1. `red_team.py`
2. `blue_team.py`
3. `provider_adapter.py`
4. `mock_provider.py`
5. `contracts.py`

Parallel ownership model:
1. Red-team: owns `red_team.py`
2. Blue-team: owns `blue_team.py`
3. Shared interface file: `contracts.py` (coordinate before edits)
