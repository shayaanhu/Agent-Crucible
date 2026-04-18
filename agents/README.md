# agents/

Contains the red-team attack logic and blue-team guardrail pipeline. Both teams share a verdict contract defined in `contracts.py`.

---

## Structure

```
agents/
├── red/                Red-team agent — generates adversarial attack prompts
├── blue/               Blue-team pipeline — detects and classifies unsafe outputs
├── contracts.py        Shared verdict schema (single source of truth)
├── providers.py        LLM provider adapters (Groq)
├── provider_adapter.py Provider interface base class
└── mock_provider.py    Deterministic mock provider used in demo mode and tests
```

---

## Red Team (`red/`)

Generates multi-turn adversarial prompts using configurable attack strategies. The red-team runtime drives the conversation loop and passes each model response to the blue-team pipeline.

**Attack strategies:**

| Strategy ID | Description |
|-------------|-------------|
| `direct_jailbreak` | Direct instruction to ignore safety guidelines |
| `instruction_override_chain` | Chain of prompts designed to override the system prompt |
| `system_prompt_probing` | Probe and extract the system prompt |
| `policy_confusion` | Exploit ambiguity in policy language |
| `roleplay_jailbreak` | Use roleplay framing to bypass guardrails |
| `context_poisoning` | Inject misleading context to shift model behavior |
| `benign_malicious_sandwich` | Wrap malicious content between benign requests |
| `multi_step_escalation` | Gradually escalate request severity across turns |

## Blue Team (`blue/`)

Runs a three-detector pipeline on each model response and aggregates the signals into a single verdict.

**Detectors:**
- **Rule Detector** — regex and keyword-based, always active
- **LlamaGuard** — Groq-hosted classifier (requires `GROQ_API_KEY`, enabled by default)
- **NeMo Guardrails** — rail-based classifier (requires `nemoguardrails` library and config path)

If LlamaGuard or NeMo are unavailable the pipeline falls back to rules-only enforcement silently.

---

## Verdict Contract

Every turn produces a verdict:

| Field | Description |
|-------|-------------|
| `allowed` | Whether the response was passed through |
| `category` | Policy category that was triggered |
| `confidence` | Aggregated confidence score (0–1) |
| `severity` | `low` / `medium` / `high` / `critical` |
| `action` | `allow` / `block` / `redact` / `escalate` |
| `reason` | Human-readable explanation |
| `policy_id` | The specific policy that fired |
| `detector_results` | Per-detector signal breakdown |

---

## Extending

**Add a new red-team strategy:**
1. Implement it in `red/red_team_strategies.py` and register it in `build_strategy_registry()`.
2. Add a fixture file at `eval/fixtures/red_team/<strategy_id>.json`.
3. Add tests in `backend/tests/test_red_team_engine.py`.

**Add a new blue-team policy:**
1. Add an entry in `config/policies.json`.
2. Restart the backend — policies are loaded at startup.
3. Add tests in `backend/tests/test_blue_team_policy_engine.py`.
