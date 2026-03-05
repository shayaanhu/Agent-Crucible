# Developer Setup (Simple Local Workflow)

## Goal
Run backend and frontend locally without Docker.

## Prerequisites
1. Python 3.11+
2. Node.js 20+
3. Git

## Repository Structure
1. `backend/`
2. `frontend/`
3. `agents/`
4. `eval/`
5. `docs/`

## Backend Setup
1. Create environment:
   `python -m venv .venv`
2. Activate environment:
   `.venv\\Scripts\\Activate.ps1`
3. Install initial packages:
   `pip install -r backend/requirements.txt`
4. From repository root, run backend:
   `python -m uvicorn backend.app.main:app --reload`

## Frontend Setup
1. From repository root, install dependencies:
   `cd frontend && npm install`
2. Start dev server:
   `npm run dev`
3. Frontend default URL:
   `http://localhost:5173`
4. Backend default URL:
   `http://localhost:8000`

## Day-to-Day Workflow
1. Pull latest `main`.
2. Make a small scoped change.
3. Run local tests and lint commands.
4. Commit and push directly to `main` (temporary process for now).

## Deferred Work
1. Docker setup is intentionally deferred.
2. CI pipeline and branch protection are intentionally deferred.
