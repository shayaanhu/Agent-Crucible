# Agent Crucible

A red-team / blue-team LLM safety testing framework. A red-team agent launches adversarial attacks against a target model; a blue-team guardrail pipeline (rule engine + LlamaGuard + NeMo Guardrails) detects and classifies unsafe outputs in real time. Everything is visible through a React dashboard.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 or newer |
| Node.js | 18 or newer |
| Groq API key | [console.groq.com](https://console.groq.com) (free) |

---

## Quickstart

### 1 — Clone and create your `.env`

```bash
git clone <repo-url>
cd Agent-Crucible
cp .env.example .env
```

Open `.env` and paste your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

That is the only required change.

### 2 — Install dependencies

```bash
# Python (from repo root)
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r backend/requirements.txt

# Node
cd frontend
npm install
cd ..
```

### 3 — Run

Open **two terminals** from the repo root.

**Terminal 1 — backend:**
```bash
# activate venv first (see step 2)
python -m uvicorn backend.app.main:app --reload
```
Backend runs at `http://localhost:8000`. Health check: `http://localhost:8000/health`

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```
Dashboard runs at `http://localhost:5173`

Open the dashboard, pick a mode, and start testing.

---

## Repository Layout

```
Agent-Crucible/
├── backend/        FastAPI service — run orchestration, guardrail pipeline, APIs
├── frontend/       React + Vite dashboard
├── agents/         Red-team and blue-team agent logic
│   ├── red/        Attack strategies and runtime
│   └── blue/       Guardrail detectors and aggregation
├── eval/           Offline evaluation and benchmarking scripts
├── config/         Policy definitions (policies.json) and NeMo config
└── docs/           Design notes and architecture references
```

---

## Testing

```bash
# activate venv first
python -m pytest backend/tests -q
python -m ruff check backend agents eval
```

---

## Evaluation Scripts

Run the red-team objective suite against a live backend:

```bash
python eval/run_red_team_dataset.py --provider groq --max-turns 3 --cooldown-seconds 10
```

See [`eval/README.md`](eval/README.md) for the full list of scripts and options.

---

## Environment Variables Reference

See [`.env.example`](.env.example) for the full list with descriptions. The only required variable is `GROQ_API_KEY`.

---

## Modes

| Mode | Description |
|------|-------------|
| **Live Attack Lab** | Multi-turn red-team simulator with strategy chains |
| **Attack Sandbox** | Write your own prompt and see the blue-team verdict |
| **Blue Team Showcase** | Demo mode — model always responds unsafely so you can watch all three detectors fire live |
| **Lab Exercises** | Guided labs with pre-configured attacks and reflection notes |
| **Testing Suite** | Automated benchmark across all attack categories |
