# agents/blue/

Blue-team guardrail pipeline. Evaluates every model response and returns an explainable verdict.

---

## Files

| File | Description |
|------|-------------|
| `blue_team.py` | Top-level pipeline — orchestrates detection and aggregation |
| `blue_team_detectors.py` | Rule Detector, LlamaGuard adapter, NeMo Guardrails adapter |
| `blue_team_aggregation.py` | Combines per-detector signals into a single verdict |
| `blue_team_policies.py` | Loads and indexes policies from `config/policies.json` |
| `blue_team_config.py` | Reads configuration from environment variables |

---

## Detection pipeline

Each model response runs through up to three detectors in parallel:

1. **Rule Detector** — pattern matching against known jailbreak signatures, banned keywords, and policy-specific regex rules. Always active.
2. **LlamaGuard** — uses Groq to run a LlamaGuard classification prompt. Active when `GROQ_API_KEY` is set and `BLUE_TEAM_ENABLE_LLAMA_GUARD=1`.
3. **NeMo Guardrails** — uses a local NeMo rails config. Active when `BLUE_TEAM_ENABLE_NEMO_GUARDRAILS=1` and `BLUE_TEAM_NEMO_CONFIG_PATH` points to a valid config directory.

If a detector's dependency is missing it returns a safe non-blocking signal and the pipeline continues without it.

## Aggregation strategies

Configured per policy in `config/policies.json`:

| Strategy | Behaviour |
|----------|-----------|
| `any_hit_blocks` | Block if any detector flags a violation (default — most conservative) |
| `majority_vote` | Block if more than half of active detectors flag |
| `weighted_average` | Weight each detector by reliability; block if weighted confidence exceeds threshold |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLUE_TEAM_ENABLE_LLAMA_GUARD` | `1` | Enable LlamaGuard detector |
| `BLUE_TEAM_ENABLE_NEMO_GUARDRAILS` | `1` | Enable NeMo Guardrails detector |
| `BLUE_TEAM_LLAMA_GUARD_MODEL` | `meta-llama/Llama-Guard-3-8B` | Override the LlamaGuard model |
| `BLUE_TEAM_NEMO_CONFIG_PATH` | _(empty)_ | Path to NeMo Guardrails config directory |
| `BLUE_TEAM_POLICY_CONFIG_PATH` | `config/policies.json` | Path to policy definitions |
