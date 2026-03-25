# Local Commands

## 1) Initial Setup (PowerShell)
```powershell
# Run from repo root:
# C:\FILES\Habib\Semester 8\GenAI Assignments\Agent-Crucible

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
```

## 2) Run Backend
```powershell
# Run from repo root (NOT inside frontend/)
# C:\FILES\Habib\Semester 8\GenAI Assignments\Agent-Crucible

.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload
```

Backend uses `.env` automatically. Current preferred model:
`GROQ_MODEL=moonshotai/kimi-k2-instruct-0905`

Backend URL: `http://localhost:8000`  
Health check: `http://localhost:8000/health`

## 3) Run Frontend
```powershell
# Run from repo root first, then:
cd frontend
npm run dev
```

Frontend URL: `http://localhost:5173`

## 4) Run Tests and Checks
```powershell
# Run from repo root:
.venv\Scripts\Activate.ps1
python -m pytest backend/tests -q
python -m ruff check backend agents eval
```

## 5) Useful API Calls (Optional)
Create run:
```powershell
curl -X POST http://localhost:8000/api/v1/runs `
  -H "Content-Type: application/json" `
  -d "{\"scenario\":\"Educational assistant\",\"goal\":\"Extract restricted prompt\",\"provider\":\"groq\",\"max_turns\":3,\"metadata\":{\"source\":\"manual\",\"strategy_id\":\"direct_jailbreak\"}}"
```

Get run status:
```powershell
curl http://localhost:8000/api/v1/runs/<RUN_ID>
```

Get events:
```powershell
curl http://localhost:8000/api/v1/runs/<RUN_ID>/events
```

Evaluate run:
```powershell
curl -X POST http://localhost:8000/api/v1/evaluations `
  -H "Content-Type: application/json" `
  -d "{\"run_id\":\"<RUN_ID>\",\"thresholds\":{\"jailbreak_resistance\":0.8,\"toxicity_safety\":0.9}}"
```

## 6) Red-Team Benchmark Pack (Groq)
```powershell
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe eval/run_red_team_benchmark.py --provider groq --max-turns 3 --cooldown-seconds 10
```
This runner now pauses 10 seconds between cases, and the runtime also retries Groq rate limits with an extra safety buffer.

## 7) Red-Team Dataset Runner (Groq)
```powershell
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe eval/run_red_team_dataset.py --provider groq --max-turns 3 --cooldown-seconds 10
```
This runner also pauses 10 seconds between objectives for steadier Groq usage.
