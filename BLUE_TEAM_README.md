# Blue Team README

Dedicated implementation plan for Blue Team in Agent Crucible.

## Implementation Status Snapshot

1. Phase 1 complete: verdict contract and schema fields are in place.
2. Phase 2 complete: rule-based detector pipeline and policy-config workflow are active.
3. Phase 3 in progress: real optional adapter paths exist for both LlamaGuard and NeMo Guardrails, and both preserve rules-only fallback.
4. Phase 5 started: evaluation supports `unsafe_block_rate`, `false_negative_rate`, `false_positive_rate`, and `policy_block_rate:<policy_id>`.
5. Fixture-driven regression coverage is active under `backend/tests/fixtures/blue_team/`.
6. Benchmark export is available via `eval/run_blue_team_benchmark.py`, writing artifacts to `eval/results/blue_team_benchmark_results.json`.
7. Current fallback behavior: if adapter dependencies are unavailable, detectors return non-blocking safe signals and RuleDetector continues as the primary enforcement path.
8. Adapter toggles:
   `BLUE_TEAM_ENABLE_LLAMA_GUARD=1` and `BLUE_TEAM_ENABLE_NEMO_GUARDRAILS=1`.
9. Optional LlamaGuard model override:
   `BLUE_TEAM_LLAMA_GUARD_MODEL=<transformers-model-id>`.
10. Optional NeMo Guardrails config path:
   `BLUE_TEAM_NEMO_CONFIG_PATH=<path-to-guardrails-config>`.

## Purpose

Blue Team is responsible for detecting unsafe model outputs, enforcing guardrail actions, and producing explainable verdicts that feed evaluation and dashboard views.

## Current State (From Codebase)

1. Baseline Blue Team agent exists in `agents/blue_team.py`.
2. Current verdict contract is: `allowed`, `category`, `confidence`, `reason` in `agents/contracts.py`.
3. Blue Team is invoked during run execution in `backend/app/pipeline.py`.
4. Verdicts are stored and later scored by `eval/scorer.py`.
5. Basic integration coverage exists in `backend/tests/test_team_contracts.py`.

## Target State

Build Blue Team as a configurable guardrail subsystem with:

1. Multi-detector policy checks (rules + model-backed guardrails).
2. Actionable decisions (`allow`, `block`, `redact`, `escalate`; `safe_rewrite` is a stretch goal — see note below).
3. Defined confidence aggregation strategy across detectors.
4. Per-turn evidence and policy traceability.
5. Evaluation-ready signals for safety benchmarking.
6. Frontend-visible guardrail explanations.

> **Note on `safe_rewrite`:** Rewriting model output safely while preserving intent is a non-trivial problem. This action is marked as a stretch goal and should not block core enforcement phases. Implement only if time permits after Phase 4.

## Architecture Plan

1. Input: model output text + run metadata.
2. Preprocessing: normalize text and extract context features.
3. Detection: rule detector, LlamaGuard adapter, NeMo Guardrails adapter.
4. Aggregation: combine detector signals into one verdict using a defined strategy (see Confidence Aggregation below).
5. Enforcement: apply action strategy for pipeline/runtime behavior.
6. Telemetry: persist detector evidence for APIs and evaluation.

## Adapter Notes

1. `LlamaGuard` in this repo is an optional classifier-style detector. If `transformers` is installed, the detector runs a local text-generation pipeline with a guardrail classification prompt and maps the result into `DetectorSignal`.
2. `NeMo Guardrails` in this repo is an optional rail-backed detector. If `nemoguardrails` is installed and `BLUE_TEAM_NEMO_CONFIG_PATH` points to a valid Guardrails config, the detector uses `RailsConfig.from_path(...)` and `LLMRails.generate(...)` to classify the output as safe or unsafe.
3. If either backend is missing or unconfigured, the detector returns a safe non-blocking fallback signal and RuleDetector remains the primary enforcement path.

## Blue Team Contracts (Planned v2)

Extend verdict schema while keeping backward compatibility.

**Existing fields:**
`allowed`, `category`, `confidence`, `reason`

**New fields:**
`action`, `severity`, `policy_id`, `detector_results`, `dry_run`

The `dry_run` flag (boolean) allows the pipeline to log what *would* have been blocked without applying enforcement. This is essential for threshold tuning and debugging (see Phase 4).

Likely touchpoints:
1. `agents/contracts.py`
2. `backend/app/schemas.py`
3. `docs/interface-contracts.md`

## Confidence Aggregation Strategy

When multiple detectors (rule engine, LlamaGuard, NeMo) each return a signal, their outputs must be combined into a single verdict. This strategy must be frozen in Phase 1 because it cascades into scoring logic, enforcement decisions, and frontend display.

**Proposed default:** `any_hit_blocks` — if any detector flags a policy violation at or above its configured threshold, the verdict is a block. This is the most conservative baseline.

**Alternatives to configure per policy:**
- `majority_vote` — block only if more than half of active detectors flag.
- `weighted_average` — weight each detector by its reliability score; block if weighted confidence exceeds threshold.

The chosen strategy per policy should be declared in the policy configuration file and respected by the aggregator.

## Policy Taxonomy (Initial)

Each policy must define: detection criteria, severity, default action, aggregation strategy, and escalation condition. Enforcement actions and policy definitions must stay cross-referenced — every action listed in a policy must correspond to a supported enforcement action.

| Policy ID | Severity | Default Action |
|---|---|---|
| `jailbreak_attempt` | high | block |
| `prompt_injection` | high | block |
| `restricted_workflow_disclosure` | medium | redact |
| `sensitive_data_exposure` | high | block |
| `unsafe_instruction_generation` | high | block |
| `toxicity_or_abuse` | medium | redact |

**Escalation condition** (applies to all): if confidence exceeds 0.95 and severity is `high`, escalate to human review queue regardless of default action.

## Supported Enforcement Actions

| Action | Description |
|---|---|
| `allow` | Pass output through unchanged. |
| `block` | Suppress output and return a policy violation message. |
| `redact` | Strip flagged content and return sanitized output. |
| `escalate` | Flag for human review; optionally block in the interim. |
| `safe_rewrite` | *(Stretch goal)* Rewrite output to comply with policy. |

## Implementation Phases

### Phase 1: Contract + Config Foundation

1. Freeze Blue Team v2 verdict schema including `dry_run` flag and aggregation strategy field.
2. Add policy configuration file (ids, thresholds, actions, aggregation strategy per policy).
3. Keep existing tests passing with fallback defaults.

### Phase 2: Rule Engine Refactor + Rules-Only Baseline

1. Refactor `agents/blue_team.py` into detector pipeline stages.
2. Move hardcoded patterns into policy-driven rule sets.
3. Return deterministic, explainable detector outputs.
4. **Lock down a rules-only baseline benchmark** — record accuracy, false positive rate, and false negative rate before any model-backed adapters are introduced. This establishes the comparison floor that Phase 3 adapters must beat.

### Phase 3: Guardrail Adapters (Stub Early, Integrate Later)

1. **By end of Week 4:** Add stub adapters for LlamaGuard and NeMo Guardrails that return mock signals. Validate the interface and aggregation pipeline against the stubs before real dependencies are introduced.
2. **Weeks 5–6:** Replace stubs with real LlamaGuard adapter.
3. **Weeks 6–7:** Replace stubs with real NeMo Guardrails adapter.
4. Support rules-only mode when adapters/dependencies are unavailable.

> **Why stub early:** LlamaGuard and NeMo are heavyweight dependencies with real setup friction. If integration issues arise late, there is no buffer. Validating interfaces against stubs by Week 4 isolates adapter problems before they affect the rest of the timeline.

### Phase 4: Enforcement + Pipeline Integration

1. Apply action semantics (`allow`, `block`, `redact`, `escalate`) in `backend/app/pipeline.py`.
2. Implement `dry_run` mode: log enforcement decisions without applying them.
3. Persist per-turn detector evidence in store/schemas.
4. Expose enriched guardrail data through events/status APIs.

### Phase 5: Evaluation + Benchmarking

1. Extend metrics beyond pass/fail ratios: false positive rate, false negative rate, per-policy block rate.
2. Compare model-backed detector accuracy against the rules-only baseline locked in Phase 2.
3. Add Blue Team fixture sets for safe/unsafe regression testing (coordinate fixture authorship with Red Team — see Fixture Hand-off section below).
4. Export benchmark artifacts for reports.

### Phase 6: Frontend Explainability

1. Show guardrail action, category, confidence, and `policy_id` per turn.
2. Show detector evidence summary and overall run risk score.
3. Support comparison views across runs.

## Fixture Hand-off: Red Team ↔ Blue Team

Red Team attack outputs are the natural source of Blue Team regression fixtures. This hand-off should be formalized:

1. Red Team exports a structured fixture file per attack type (turn history + expected violation category).
2. Blue Team ingests fixtures into `backend/tests/fixtures/` and asserts correct detection and action.
3. Both teams agree on the fixture schema by end of Week 3 so fixture production can begin in parallel.

This prevents duplication of effort and ensures Blue Team regression tests reflect real attack patterns.

## File Ownership Map

| File | Owner |
|---|---|
| `agents/blue_team.py` | Core detector logic |
| `agents/contracts.py` | Shared verdict contracts |
| `backend/app/pipeline.py` | Orchestration + enforcement integration |
| `backend/app/schemas.py` | API schemas |
| `backend/app/store.py` | Persistence layer |
| `eval/scorer.py` | Evaluation scoring |
| `frontend/src/App.jsx` | Frontend guardrail display |
| `backend/tests/` | All test suites |
| `config/policies.yaml` | Policy configuration (new) |

## Testing Plan

1. Unit tests for each detector and aggregator logic.
2. Contract tests for Blue Team verdict shape, field ranges, and aggregation strategy behavior.
3. Integration tests for run pipeline with safe/unsafe outputs, including `dry_run` mode.
4. Regression tests from Red Team fixture packs for known jailbreak patterns.
5. Metric correctness tests for extended evaluation scoring.
6. Baseline comparison tests: rules-only accuracy vs. model-backed accuracy per policy.

**Commands:**
```powershell
.venv\Scripts\Activate.ps1
python -m pytest backend/tests -q
python -m ruff check backend agents eval
.venv\Scripts\python.exe eval/run_blue_team_benchmark.py
```

## Week-by-Week Blue Team Roadmap

| Week | Deliverable |
|---|---|
| Week 3 | Contract v2 + policy config + rule-engine baseline + rules-only benchmark |
| Week 4 | Stub adapters validated + pipeline enforcement actions + `dry_run` mode + telemetry fields |
| Week 5 | Metrics expansion + Blue Team fixture benchmarking against rules-only baseline |
| Week 6 | LlamaGuard real adapter + fallback behavior |
| Week 7 | NeMo Guardrails real adapter + frontend guardrail explainability views |
| Week 8 | Hardening, threshold tuning, false-positive reduction using `dry_run` logs |
| Week 9 | Final docs, demo pack, and release readiness |

## Definition of Done (Blue Team)

1. Blue Team produces policy-based, explainable verdicts per turn with a defined confidence aggregation strategy.
2. Enforcement actions (`allow`, `block`, `redact`, `escalate`) are applied consistently in pipeline execution.
3. `dry_run` mode is functional and used during threshold tuning.
4. Metrics quantify safety performance versus the rules-only baseline and track regressions.
5. Frontend exposes guardrail outcomes clearly for review.
6. Tests cover contract, logic, integration, metric behavior, and Red Team fixture regression.
7. Adapter fallback to rules-only mode is verified when model-backed detectors are unavailable.

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Optional for OpenAI-backed runtime:
```powershell
$env:OPENAI_API_KEY="your_key_here"
$env:OPENAI_MODEL="gpt-4o-mini"
```
