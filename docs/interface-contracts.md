# Interface Contracts (Frozen for Week 2 Start)

## API Endpoints
1. `POST /api/v1/runs`
2. `GET /api/v1/runs/{run_id}`
3. `GET /api/v1/runs/{run_id}/events`
4. `POST /api/v1/evaluations`

## RunCreateRequest
```json
{
  "scenario": "string",
  "goal": "string",
  "provider": "string",
  "max_turns": 3,
  "metadata": {
    "course": "string",
    "team": "string"
  }
}
```

## RunCreateResponse
```json
{
  "run_id": "string",
  "status": "queued",
  "created_at": "2026-03-06T00:00:00Z"
}
```

## RunStatusResponse
```json
{
  "run_id": "string",
  "status": "queued | running | completed | failed",
  "provider": "string",
  "summary": "string",
  "created_at": "2026-03-06T00:00:00Z"
}
```

## RunEventsResponse
```json
{
  "run_id": "string",
  "events": [
    {
      "turn_index": 1,
      "input": "string",
      "model_output": "string",
      "timestamp": "2026-03-06T00:00:00Z"
    }
  ]
}
```

## EvaluationRequest
```json
{
  "run_id": "string",
  "thresholds": {
    "jailbreak_resistance": 0.8,
    "toxicity_safety": 0.9
  }
}
```

## EvaluationResponse
```json
{
  "run_id": "string",
  "metrics": [
    {
      "metric_name": "jailbreak_resistance",
      "value": 0.75,
      "threshold": 0.8,
      "pass_fail": "fail"
    }
  ],
  "overall": "fail"
}
```

## Core Types
1. `AttackPrompt`: `id`, `scenario`, `goal`, `payload`, `metadata`
2. `AttackTurn`: `turn_index`, `input`, `model_output`, `timestamp`
3. `GuardrailVerdict`: `allowed`, `category`, `confidence`, `reason`
4. `RunRecord`: `run_id`, `provider`, `status`, `created_at`, `summary`
5. `EvalMetric`: `metric_name`, `value`, `threshold`, `pass_fail`

## State Machine
1. `queued -> running -> completed`
2. `queued -> running -> failed`

## Notes
1. Provider adapter is interface-first and provider-agnostic.
2. Week 2 implements one concrete provider and one mock mode.
