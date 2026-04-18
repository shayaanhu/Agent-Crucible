# frontend/

React + Vite dashboard for the Agent Crucible testing framework.

---

## Running

From the repo root:

```bash
cd frontend
npm install   # first time only
npm run dev
```

Dashboard runs at `http://localhost:5173`. The backend must also be running at `http://localhost:8000`.

---

## Structure

```
frontend/
├── src/
│   ├── App.jsx               Root — routing between modes
│   ├── features/
│   │   ├── EntryView.jsx     Mode selection screen
│   │   ├── lab/              Live Attack Lab
│   │   ├── sandbox/          Attack Sandbox
│   │   ├── demo/             Blue Team Showcase (demo mode)
│   │   ├── labs/             Lab Exercises
│   │   └── evaluation/       Testing Suite and results
│   ├── components/           Shared UI components
│   ├── constants/            API base URL and shared constants
│   ├── utils/                Formatting and analysis helpers
│   ├── icons/                Icon wrappers
│   └── styles.css            Global design system
├── index.html
└── vite.config.js
```

## Build

```bash
npm run build   # outputs to dist/
npm run preview # serve the production build locally
```
