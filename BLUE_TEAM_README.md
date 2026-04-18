# Blue Team — Implementation Guide

The blue-team pipeline evaluates every model response in real time and produces an explainable guardrail verdict. It runs three detectors in parallel and aggregates their signals according to per-policy rules.

For setup and environment variables see [`agents/blue/README.md`](agents/blue/README.md).

---

## Architecture

```
Model response
      │
      ▼
┌─────────────────────────────────────┐
│           Blue Team Pipeline        │
│                                     │
│  ┌─────────────┐                    │
│  │ Rule        │  Always active.    │
│  │ Detector    │  Pattern matching. │
│  └─────────────┘                    │
│  ┌─────────────┐                    │
│  │ LlamaGuard  │  Groq-hosted.      │
│  │ Detector    │  Optional.         │
│  └─────────────┘                    │
│  ┌─────────────┐                    │
│  │ NeMo        │  Local rails.      │
│  │ Guardrails  │  Optional.         │
│  └─────────────┘                    │
│            │                        │
│     Aggregator                      │
│  (any_hit / majority / weighted)    │
└─────────────────────────────────────┘
      │
      ▼
   Verdict
(allowed, category, severity, action, confidence, reason, policy_id)
```

---

## Policies

Policies are defined in [`config/policies.json`](config/policies.json). Each policy maps to a severity level and a default enforcement action:

| Policy ID | Severity | Default Action |
|-----------|----------|----------------|
| `jailbreak_attempt` | high | block |
| `prompt_injection` | high | block |
| `restricted_workflow_disclosure` | medium | redact |
| `sensitive_data_exposure` | high | block |
| `unsafe_instruction_generation` | high | block |
| `toxicity_or_abuse` | medium | redact |

---

## Evaluation

```bash
# Blue-team objective suite
python eval/run_blue_team_dataset.py --provider groq --cooldown-seconds 10

# Regression benchmark
python eval/run_blue_team_benchmark.py

# Markdown report
python eval/report_blue_team_eval.py --input eval/results/blue_team_benchmark_results.json
```

---

## Testing

```bash
python -m pytest backend/tests -q
```

Key test files:
- `backend/tests/test_blue_team_policy_engine.py` — policy loading and rule matching
- `backend/tests/test_team_contracts.py` — verdict schema validation
- `backend/tests/fixtures/blue_team/` — regression fixtures for known unsafe patterns
