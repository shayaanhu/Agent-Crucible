# Testing Strategy (Week 1 Baseline)

## Objective
Define the minimum testing plan that guards contracts and behavior before feature expansion.

## Test Categories
1. Contract tests for API request/response schemas.
2. Unit tests for run lifecycle transitions.
3. Unit tests for guardrail verdict consistency.
4. Unit tests for evaluation metric calculations.
5. Frontend component tests with mocked API payloads.
6. Local smoke test for backend startup and health endpoint.

## Priority Scenarios
1. Valid run request creates a queued run.
2. Invalid run request returns validation error.
3. Run transitions follow allowed state machine only.
4. Known unsafe prompt fixture is flagged by guardrail.
5. Evaluation compares metric value to threshold correctly.
6. Frontend timeline renders ordered run events.

## Manual Quality Gate (No CI Yet)
1. Run backend tests locally before each push.
2. Run frontend tests and build locally before each push.
3. Verify contract examples in `docs/interface-contracts.md` still match implementation.
4. Log test command outputs in your local notes for traceability.

## Commands
1. Backend tests: `python -m pytest backend/tests -q`
2. Backend lint: `python -m ruff check backend agents eval`
3. Frontend build check: `npm run build`
