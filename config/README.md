# config/

Runtime configuration for the blue-team guardrail pipeline.

---

## Files

### `policies.json`

Defines every guardrail policy. The blue-team pipeline loads this at startup.

Each policy entry specifies:
- `id` — unique policy identifier referenced in verdicts
- `severity` — `low` / `medium` / `high` / `critical`
- `action` — default enforcement action (`allow` / `block` / `redact` / `escalate`)
- `aggregation_strategy` — how multiple detector signals are combined (`any_hit_blocks`, `majority_vote`, `weighted_average`)
- `patterns` — regex rules used by the Rule Detector

To add or modify a policy, edit this file and restart the backend.

### `nemo/`

Optional NeMo Guardrails configuration directory. Only needed if you are running the NeMo detector. Set `BLUE_TEAM_NEMO_CONFIG_PATH=config/nemo` in your `.env` to activate it.
