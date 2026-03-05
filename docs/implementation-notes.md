# Implementation Notes (Merged)

## What This Replaces
This file merges the high-level content previously spread across:
1. Week 1 scope notes
2. Architecture baseline notes
3. Threat model baseline notes
4. Workflow/ADR process notes

## Current Build Goal
Implement a minimal vertical slice that is runnable locally:
1. Create a run
2. Execute one mock red-team attack turn
3. Apply one blue-team safety verdict
4. Return run status and event history
5. Compute threshold-based evaluation metrics

## Working Decisions
1. Monorepo layout: `backend/`, `frontend/`, `agents/`, `eval/`, `docs/`
2. Stack: FastAPI backend + React frontend
3. Workflow: simple direct pushes to `main` for now
4. No Docker and no CI in current phase
5. Provider design: provider-agnostic interface, one mock provider implementation first

## System Shape
1. Frontend calls backend APIs only.
2. Backend owns run lifecycle and orchestration.
3. `agents/` contains red-team, blue-team, and provider adapter logic.
4. `eval/` contains metric scoring logic used by the evaluation endpoint.

## Team Split (Parallel Development)
1. Red-team owner works in `agents/red_team.py` and only exposes `get_red_team_agent()` with `build_attack_prompt(...)`.
2. Blue-team owner works in `agents/blue_team.py` and only exposes `get_blue_team_agent()` with `evaluate_output(...)`.
3. Backend orchestrator (`backend/app/pipeline.py`) consumes both through contracts, not internal implementation details.
4. Shared change surface is `agents/contracts.py`; changes here require both owners to sync.
5. Contract safety net: `backend/tests/test_team_contracts.py` verifies end-to-end compatibility.

## Threat Focus for Initial Slice
1. Jailbreak-style prompt attempts
2. Unsafe output detection and blocking verdicts
3. Basic logging of attack/response events for review

## MVP Acceptance
1. All four planned API endpoints are implemented.
2. Run lifecycle reaches `completed` or `failed`.
3. Event timeline endpoint returns turn data.
4. Evaluation endpoint returns metric values, thresholds, and pass/fail.
5. Frontend can create a run, view status/events, and request evaluation.
