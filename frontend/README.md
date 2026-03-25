# Frontend

React dashboard for:
1. Starting test runs
2. Viewing run status
3. Inspecting event timelines
4. Viewing evaluation summaries

Run locally:
1. `cd frontend`
2. `npm install`
3. `npm run dev`

Dry-run testing from UI:
1. Enable the `Dry-run mode` checkbox before creating a run.
2. Create and refresh a run to view timeline verdicts.
3. In dry-run mode, unsafe outputs are logged with `would block` metadata but are not enforced as blocked actions.

Benchmark tuning from UI:
1. Enter a `Benchmark Label` in the main form.
2. Click `Run Benchmark` to generate a labeled Blue Team benchmark artifact.
3. Use the benchmark and history panels to compare the latest run against earlier labeled runs.
