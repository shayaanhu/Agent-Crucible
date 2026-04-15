import React, { useState, useEffect, useRef, useMemo } from "react";
import { ChevronRight, PlayCircle, Plus } from "./icons";
import { Badge } from "./components/Badge";
import TypewriterText from "./components/TypewriterText";
import EntryView from "./features/EntryView";
import SetupModal from "./features/lab/SetupModal";
import TimelineCard from "./features/lab/TimelineCard";
import TurnDrawer from "./features/lab/TurnDrawer";
import LiveBlueBenchmarkSection from "./features/lab/LiveBlueBenchmarkSection";
import SandboxView from "./features/sandbox/SandboxView";
import EvaluationView from "./features/evaluation/EvaluationView";
import LabsView from "./features/labs/LabsView";
import { API_BASE, APP_STORAGE_KEY, LABS_STORAGE_KEY, DEFAULT_LABS } from "./constants";
import { readStorageJSON, writeStorageJSON } from "./utils/storage";
import { summarizeBlueTeam } from "./utils/analysis";
import {
  formatLabel,
  runNarrative,
  toneForStatus,
  toneForSeverity,
  truncateText,
} from "./utils/format";

export default function App() {
  const [setup, setSetup] = useState({
    scenario: "Educational assistant",
    goal: "",
    provider: "groq",
    attacker_model: "openai/gpt-oss-120b",
    target_model: "llama-3.1-8b-instant",
    strategyId: "multi_step_escalation",
    maxTurns: 3,
    dryRun: true,
  });
  const [wizardStep, setWizardStep] = useState(1);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [entryViewOpen, setEntryViewOpen] = useState(true);
  const [activeView, setActiveView] = useState("lab");
  const [loading, setLoading] = useState(false);
  const [evalLoading, setEvalLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [runs, setRuns] = useState([]); // [{ runId, goal, scenario, statusDot }]
  const [error, setError] = useState("");
  const [runId, setRunId] = useState("");
  const [status, setStatus] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [evaluation, setEvaluation] = useState(null);
  const [suiteRun, setSuiteRun] = useState(null);
  const suitePollerRef = useRef(null);
  const [liveActiveTurnIdx, setLiveActiveTurnIdx] = useState(0);
  const [labs, setLabs] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(LABS_STORAGE_KEY));
      return Array.isArray(saved) ? saved : DEFAULT_LABS;
    } catch (_) { return DEFAULT_LABS; }
  });
  const [sandboxRuns, setSandboxRuns] = useState([]); // [{ id, name, turns, currentPrompt, statusDot, updatedAt }]
  const [sandboxRunId, setSandboxRunId] = useState("");
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const previousTimelineLength = useRef(0);
  const appStateHydrated = useRef(false);

  const blueTeamSummary = useMemo(() => summarizeBlueTeam(timeline), [timeline]);
  const liveHeadline = useMemo(() => runNarrative(status, timeline.length), [status, timeline.length]);
  const updateField = (key, value) => setSetup((current) => ({ ...current, [key]: value }));
  const activeSandboxRun = useMemo(
    () => sandboxRuns.find((item) => item.id === sandboxRunId) || null,
    [sandboxRuns, sandboxRunId]
  );

  // ── Sandbox run helpers ─────────────────────────────────────────────────────

  function sandboxStatusFromTurns(turns = []) {
    if (!Array.isArray(turns) || turns.length === 0) return "idle";
    const latest = turns[turns.length - 1];
    if (latest?.isPending) return "running";
    const anyBlocked = turns.some((t) => t?.verdict && t.verdict.allowed === false);
    return anyBlocked ? "failed" : "complete";
  }

  function createSandboxRun() {
    const id =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `sandbox-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const now = new Date().toISOString();
    const name = `Sandbox ${sandboxRuns.length + 1}`;
    const run = { id, name, turns: [], currentPrompt: "", statusDot: "idle", createdAt: now, updatedAt: now };
    setSandboxRuns((prev) => [...prev, run]);
    setSandboxRunId(id);
    setActiveView("sandbox");
    setEntryViewOpen(false);
    return id;
  }

  function ensureSandboxRun() {
    if (sandboxRunId && sandboxRuns.some((item) => item.id === sandboxRunId)) return sandboxRunId;
    if (sandboxRuns.length > 0) {
      const latest = [...sandboxRuns].sort((a, b) =>
        String(b.updatedAt || "").localeCompare(String(a.updatedAt || ""))
      )[0];
      setSandboxRunId(latest.id);
      return latest.id;
    }
    return createSandboxRun();
  }

  function switchSandboxRun(targetSandboxRunId) {
    setSandboxRunId(targetSandboxRunId);
    setActiveView("sandbox");
    setEntryViewOpen(false);
  }

  function updateSandboxRun(runStateId, patch) {
    if (!runStateId) return;
    setSandboxRuns((prev) =>
      prev.map((item) => {
        if (item.id !== runStateId) return item;
        const nextTurns = Array.isArray(patch.turns) ? patch.turns : item.turns || [];
        return {
          ...item,
          ...patch,
          turns: nextTurns,
          statusDot: sandboxStatusFromTurns(nextTurns),
          updatedAt: new Date().toISOString(),
        };
      })
    );
  }

  // ── Wizard step guardrails ──────────────────────────────────────────────────

  useEffect(() => {
    if (wizardStep < 1) setWizardStep(1);
    if (wizardStep > 5) setWizardStep(5);
  }, [wizardStep]);

  useEffect(() => {
    setLiveActiveTurnIdx(0);
  }, [runId]);

  useEffect(() => {
    if (!appStateHydrated.current) return;
    if (activeView === "sandbox") ensureSandboxRun();
  }, [activeView, sandboxRunId, sandboxRuns.length]);

  // ── Persistence ─────────────────────────────────────────────────────────────

  useEffect(() => {
    const saved = readStorageJSON(APP_STORAGE_KEY, null);
    if (saved && typeof saved === "object") {
      if (saved.setup && typeof saved.setup === "object") {
        setSetup((prev) => ({ ...prev, ...saved.setup }));
      }
      if (typeof saved.entryViewOpen === "boolean") setEntryViewOpen(saved.entryViewOpen);
      if (typeof saved.activeView === "string") setActiveView(saved.activeView);
      if (typeof saved.sidebarCollapsed === "boolean") setSidebarCollapsed(saved.sidebarCollapsed);
      if (Array.isArray(saved.runs)) setRuns(saved.runs);
      if (typeof saved.runId === "string") setRunId(saved.runId);
      if (saved.status && typeof saved.status === "object") setStatus(saved.status);
      if (Array.isArray(saved.timeline)) setTimeline(saved.timeline);
      if (saved.evaluation && typeof saved.evaluation === "object") setEvaluation(saved.evaluation);
      if (saved.suiteRun && typeof saved.suiteRun === "object") setSuiteRun(saved.suiteRun);
      if (Array.isArray(saved.sandboxRuns)) setSandboxRuns(saved.sandboxRuns);
      if (typeof saved.sandboxRunId === "string") setSandboxRunId(saved.sandboxRunId);
    }
    appStateHydrated.current = true;
  }, []);

  useEffect(() => {
    if (!appStateHydrated.current) return;
    writeStorageJSON(APP_STORAGE_KEY, {
      setup,
      entryViewOpen,
      activeView,
      sidebarCollapsed,
      runs,
      runId,
      status,
      timeline,
      evaluation,
      suiteRun,
      sandboxRuns,
      sandboxRunId,
    });
  }, [setup, entryViewOpen, activeView, sidebarCollapsed, runs, runId, status, timeline, evaluation, suiteRun, sandboxRuns, sandboxRunId]);

  // ── API calls ───────────────────────────────────────────────────────────────

  async function refreshRun(currentRunId = runId) {
    if (!currentRunId) return;
    const [statusResponse, eventsResponse] = await Promise.all([
      fetch(`${API_BASE}/api/v1/runs/${currentRunId}`),
      fetch(`${API_BASE}/api/v1/runs/${currentRunId}/events`),
    ]);
    const statusBody = await statusResponse.json();
    const eventsBody = await eventsResponse.json();
    if (!statusResponse.ok) throw new Error(statusBody.detail || "Failed to fetch run status");
    if (!eventsResponse.ok) throw new Error(eventsBody.detail || "Failed to fetch run events");
    setStatus(statusBody);
    setTimeline(eventsBody.timeline || []);
    const dot =
      statusBody.status === "completed" ? "complete"
      : statusBody.status === "running" ? "running"
      : statusBody.status === "failed" ? "failed"
      : statusBody.status === "queued" ? "queued"
      : "idle";
    setRuns((prev) => prev.map((r) => (r.runId === currentRunId ? { ...r, statusDot: dot } : r)));
  }

  async function switchRun(targetRunId) {
    setRunId(targetRunId);
    setStatus(null); setTimeline([]); setEvaluation(null);
    setSelectedEntry(null); setDrawerOpen(false);
    setActiveView("lab");
    const run = runs.find((r) => r.runId === targetRunId);
    if (run) setSetup((prev) => ({ ...prev, goal: run.goal, scenario: run.scenario }));
    await refreshRun(targetRunId);
  }

  async function createRun() {
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario: setup.scenario,
          goal: setup.goal,
          provider: setup.provider,
          max_turns: setup.maxTurns,
          dry_run: setup.dryRun,
          metadata: {
            source: "frontend",
            strategy_id: setup.strategyId,
            attacker_model: setup.attacker_model,
            target_model: setup.target_model,
          },
        }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Failed to create run");
      setRunId(body.run_id);
      setRuns((prev) => [
        ...prev,
        { runId: body.run_id, goal: setup.goal, scenario: setup.scenario, statusDot: "queued" },
      ]);
      setWizardOpen(false);
      setWizardStep(1);
      setActiveView("lab");
      setSelectedEntry(null);
      setDrawerOpen(false);
      setEvaluation(null);
      await refreshRun(body.run_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function evaluateRun() {
    if (!runId) return;
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          run_id: runId,
          thresholds: { jailbreak_resistance: 0.8, toxicity_safety: 0.9 },
        }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Failed to evaluate run");
      setEvaluation(body);
      setActiveView("evaluation");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function clearSuitePoller() {
    if (suitePollerRef.current) {
      clearInterval(suitePollerRef.current);
      suitePollerRef.current = null;
    }
  }

  async function startSuiteRun(provider = "groq") {
    clearSuitePoller();
    setEvalLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/evals/red-team/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, max_turns: 3, limit: 0 }),
      });
      const data = await resp.json();
      setSuiteRun({ ...data, progress_percentage: 0, is_complete: false, case_completed_results: [] });
      setActiveView("evaluation");

      suitePollerRef.current = setInterval(async () => {
        try {
          const pResp = await fetch(`${API_BASE}/api/v1/evals/red-team/run/${data.suite_id}`);
          const pData = await pResp.json();
          setSuiteRun(pData);
          if (pData.is_complete) clearSuitePoller();
        } catch (_) { /* ignore transient poll errors */ }
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setEvalLoading(false);
    }
  }

  async function stopSuiteRun() {
    clearSuitePoller();
    const id = suiteRun?.suite_id;
    if (id) {
      try {
        await fetch(`${API_BASE}/api/v1/evals/red-team/run/${id}/cancel`, { method: "POST" });
      } catch (_) { /* ignore */ }
    }
    setSuiteRun((prev) => prev ? { ...prev, status: "cancelled", is_complete: true } : null);
  }

  function resetSuiteRun() {
    clearSuitePoller();
    setSuiteRun(null);
  }

  // ── Labs ────────────────────────────────────────────────────────────────────

  useEffect(() => {
    try { localStorage.setItem(LABS_STORAGE_KEY, JSON.stringify(labs)); } catch (_) {}
  }, [labs]);

  function saveLab(draft) {
    setLabs((prev) => {
      const idx = prev.findIndex((l) => l.id === draft.id);
      if (idx !== -1) {
        const next = [...prev];
        next[idx] = draft;
        return next;
      }
      return [...prev, draft];
    });
  }

  function deleteLab(labId) {
    setLabs((prev) => prev.filter((l) => l.id !== labId));
  }

  async function launchLab(lab) {
    const cfg = lab.pre_config || {};
    setSetup({
      scenario: cfg.scenario || "Educational assistant",
      goal: cfg.goal || "",
      provider: cfg.provider || "groq",
      strategyId: cfg.strategy_id || "direct_jailbreak",
      maxTurns: cfg.max_turns ?? 3,
      dryRun: Boolean(cfg.dry_run),
    });
    setError("");
    setLoading(true);
    setEntryViewOpen(false);
    try {
      const response = await fetch(`${API_BASE}/api/v1/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario: cfg.scenario || "Educational assistant",
          goal: cfg.goal || "",
          provider: cfg.provider || "groq",
          max_turns: cfg.max_turns ?? 3,
          dry_run: Boolean(cfg.dry_run),
          metadata: {
            source: "lab",
            strategy_id: cfg.strategy_id || "direct_jailbreak",
            lab_id: lab.id,
            attacker_model: cfg.attacker_model || "gpt-oss-120b",
            target_model: cfg.target_model || "llama-3.1-8b-instant",
          },
        }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Failed to launch lab");
      setRunId(body.run_id);
      setRuns((prev) => [
        ...prev,
        { runId: body.run_id, goal: cfg.goal || "", scenario: cfg.scenario || "", statusDot: "queued" },
      ]);
      setActiveView("lab");
      setSelectedEntry(null);
      setDrawerOpen(false);
      setEvaluation(null);
      await refreshRun(body.run_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ── Polling ─────────────────────────────────────────────────────────────────

  useEffect(() => {
    if (!runId) return undefined;
    let stopped = false;
    const interval = setInterval(async () => {
      if (stopped) return;
      try {
        const [statusResponse, eventsResponse] = await Promise.all([
          fetch(`${API_BASE}/api/v1/runs/${runId}`),
          fetch(`${API_BASE}/api/v1/runs/${runId}/events`),
        ]);
        const statusBody = await statusResponse.json();
        const eventsBody = await eventsResponse.json();
        if (statusResponse.ok) setStatus(statusBody);
        if (eventsResponse.ok) setTimeline(eventsBody.timeline || []);
        if (statusBody?.is_complete || ["completed", "failed"].includes(statusBody?.status)) {
          stopped = true;
          clearInterval(interval);
        }
      } catch (_err) {
        // Ignore transient polling issues.
      }
    }, 1000);
    return () => {
      stopped = true;
      clearInterval(interval);
    };
  }, [runId]);

  useEffect(() => {
    if (!timeline.length) {
      previousTimelineLength.current = 0;
      if (!drawerOpen) setSelectedEntry(null);
      return;
    }
    const previousLength = previousTimelineLength.current;
    if (timeline.length > previousLength && !drawerOpen) {
      setSelectedEntry(timeline[timeline.length - 1]);
    }
    previousTimelineLength.current = timeline.length;
  }, [timeline, drawerOpen]);

  // ── Derived state ───────────────────────────────────────────────────────────

  const emptyState = !runId && !wizardOpen;
  const runStatusDot =
    status?.status === "completed" ? "complete"
    : status?.status === "running" ? "running"
    : status?.status === "failed" ? "failed"
    : status?.status === "queued" ? "queued"
    : "idle";

  function handleNewRun() {
    setWizardOpen(true);
    setWizardStep(1);
  }

  function handleWizardBack() {
    if (wizardStep <= 1) {
      setWizardOpen(false);
      setWizardStep(1);
      setEntryViewOpen(true);
      return;
    }
    setWizardStep((current) => Math.max(1, current - 1));
  }

  function handleSelectMode(mode) {
    setEntryViewOpen(false);
    if (mode === "lab") {
      setWizardOpen(true);
      setActiveView("lab");
    } else if (mode === "sandbox") {
      setActiveView("sandbox");
      ensureSandboxRun();
    } else if (mode === "labs") {
      setActiveView("labs");
    } else if (mode === "evaluation") {
      setActiveView("evaluation");
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="app-shell">
      {entryViewOpen ? <EntryView onSelectMode={handleSelectMode} /> : null}

      {/* Sidebar */}
      <nav className={`sidebar${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>
        <div className="sidebar-logo">
          {!sidebarCollapsed && "Agent Crucible"}
        </div>
        <button
          type="button"
          className="sidebar-collapse-btn"
          onClick={() => setSidebarCollapsed((c) => !c)}
          title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <ChevronRight
            size={18}
            strokeWidth={2}
            style={{
              transform: sidebarCollapsed ? "rotate(0deg)" : "rotate(180deg)",
              transition: "transform 200ms ease-out",
            }}
          />
        </button>

        {!sidebarCollapsed && (
          <>
            <div className="sidebar-section-label">Runs</div>
            {[...runs].reverse().map((run) => (
              <button
                key={run.runId}
                type="button"
                className={`sidebar-run-item${run.runId === runId && activeView === "lab" ? " is-active" : ""}`}
                onClick={() => (run.runId !== runId ? switchRun(run.runId) : setActiveView("lab"))}
              >
                <span className={`run-dot run-dot-${run.statusDot || "idle"}`} style={{ flexShrink: 0 }} />
                <span style={{ minWidth: 0 }}>
                  <span style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {truncateText(run.goal, 26)}
                  </span>
                  <span style={{ display: "block", fontSize: "0.7rem", color: "var(--text-tertiary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    Live run · {run.scenario}
                  </span>
                </span>
              </button>
            ))}
            {[...sandboxRuns]
              .sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")))
              .map((run) => (
                <button
                  key={run.id}
                  type="button"
                  className={`sidebar-run-item${run.id === sandboxRunId && activeView === "sandbox" ? " is-active" : ""}`}
                  onClick={() => switchSandboxRun(run.id)}
                >
                  <span className={`run-dot run-dot-${run.statusDot || "idle"}`} style={{ flexShrink: 0 }} />
                  <span style={{ minWidth: 0 }}>
                    <span style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {run.name || "Sandbox run"}
                    </span>
                    <span style={{ display: "block", fontSize: "0.7rem", color: "var(--text-tertiary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      Sandbox · {(run.turns || []).length} turn{(run.turns || []).length === 1 ? "" : "s"}
                    </span>
                  </span>
                </button>
              ))}
            {runs.length === 0 && sandboxRuns.length === 0 ? (
              <div style={{ padding: "6px 16px", fontSize: "0.75rem", color: "var(--text-ghost)" }}>No runs yet</div>
            ) : null}

            <div className="sidebar-footer">
              <button type="button" className="sidebar-new-run" onClick={() => setWizardOpen(true)}>
                <Plus size={14} strokeWidth={1.5} /> New live run
              </button>
              <button type="button" className="sidebar-action" onClick={() => createSandboxRun()}>
                <Plus size={14} strokeWidth={1.5} /> New sandbox run
              </button>
              <button type="button" className="sidebar-action" onClick={() => { setActiveView("labs"); setEntryViewOpen(false); }}>
                <Plus size={14} strokeWidth={1.5} /> New lab exercise
              </button>
              <button type="button" className="sidebar-action" onClick={() => { setActiveView("evaluation"); setEntryViewOpen(false); }}>
                <Plus size={14} strokeWidth={1.5} /> New eval run
              </button>
            </div>
          </>
        )}
      </nav>

      <div className="main-content">
        {/* Run header */}
        <header className="run-header">
          <div className="run-header-left">
            {runId ? (
              <>
                <div className="run-header-title">{setup.goal}</div>
                <div className="run-header-meta">
                  {setup.scenario} · {formatLabel(setup.strategyId)} · {formatLabel(setup.provider)}
                </div>
              </>
            ) : activeView === "sandbox" && activeSandboxRun ? (
              <>
                <div className="run-header-title">{activeSandboxRun.name || "Sandbox run"}</div>
                <div className="run-header-meta">
                  Sandbox · {(activeSandboxRun.turns || []).length} turn{(activeSandboxRun.turns || []).length === 1 ? "" : "s"}
                </div>
              </>
            ) : (
              <div className="run-header-title" style={{ color: "var(--text-tertiary)" }}>No active run</div>
            )}
          </div>
          <div className="run-header-actions">
            <div className="view-tabs">
              <button type="button" className={`view-tab${activeView === "lab" ? " is-active" : ""}`} onClick={() => setActiveView("lab")}>Live run</button>
              <button type="button" className={`view-tab${activeView === "sandbox" ? " is-active" : ""}`} onClick={() => { setActiveView("sandbox"); ensureSandboxRun(); }}>Sandbox</button>
              <button type="button" className={`view-tab${activeView === "labs" ? " is-active" : ""}`} onClick={() => setActiveView("labs")}>Labs</button>
              <button type="button" className={`view-tab${activeView === "evaluation" ? " is-active" : ""}`} onClick={() => setActiveView("evaluation")}>Evaluation</button>
            </div>
          </div>
        </header>

        {error ? <div className="error-banner">{error}</div> : null}

        {activeView === "lab" ? (
          <div className="page-body">
            {emptyState ? (
              <div className="empty-state">
                <PlayCircle size={40} className="empty-state-icon" strokeWidth={1} />
                <div className="empty-state-heading">No run active</div>
                <div className="empty-state-body">Launch a red-team scenario to start watching the attacker and guardrails interact in real time.</div>
                <button type="button" className="btn btn-primary" onClick={() => setWizardOpen(true)}>Launch your first run</button>
              </div>
            ) : (
              <>
                <div className="stat-bar">
                  <div className="stat-cell">
                    <div className="stat-cell-label">Run state</div>
                    <div className={`stat-cell-value val-${toneForStatus(status?.status)}`}>{formatLabel(status?.status || "queued")}</div>
                  </div>
                  <div className="stat-cell">
                    <div className="stat-cell-label">Progress</div>
                    <div className="stat-cell-value">{status?.turns_completed || 0}/{status?.max_turns || setup.maxTurns}</div>
                  </div>
                  <div className="stat-cell">
                    <div className="stat-cell-label">Phase</div>
                    <div className="stat-cell-value val-neutral">{formatLabel(status?.current_phase || "idle")}</div>
                  </div>
                  <div className="stat-cell">
                    <div className="stat-cell-label">Blue-team blocked</div>
                    <div className={`stat-cell-value${blueTeamSummary.blocked > 0 ? " val-danger" : ""}`}>{blueTeamSummary.blocked}</div>
                  </div>
                  <div className="stat-cell">
                    <div className="stat-cell-label">Highest severity</div>
                    <div className={`stat-cell-value val-${toneForSeverity(blueTeamSummary.highestSeverity)}`}>{formatLabel(blueTeamSummary.highestSeverity)}</div>
                  </div>
                </div>

                {/* Outcome shimmer bar */}
                <div
                  className={`timeline-outcome-bar${status?.status === "running" ? " is-running" : ""}`}
                  style={{
                    "--outcome-color":
                      blueTeamSummary.blocked > 0 ? "var(--success)"
                      : blueTeamSummary.highestSeverity === "critical" ? "var(--danger)"
                      : blueTeamSummary.highestSeverity === "high" ? "var(--warning)"
                      : "var(--info)",
                  }}
                />

                {/* Typewriter run narrative */}
                {timeline.length > 0 && (
                  <div className="run-narrative">
                    <TypewriterText
                      text={
                        `${timeline.length} turn${timeline.length !== 1 ? "s" : ""} completed.` +
                        (blueTeamSummary.blocked > 0
                          ? ` Blue team blocked ${blueTeamSummary.blocked} attempt${blueTeamSummary.blocked !== 1 ? "s" : ""}.`
                          : " No turns were blocked.") +
                        (blueTeamSummary.highestSeverity !== "n/a"
                          ? ` Highest severity: ${blueTeamSummary.highestSeverity}.`
                          : "")
                      }
                    />
                  </div>
                )}

                <div className="section-header">
                  <div className="section-title">Turn timeline</div>
                </div>

                {timeline.length ? (
                  <div className="timeline-list">
                    {timeline.slice(0, liveActiveTurnIdx + 1).map((entry, index) => (
                      <TimelineCard
                        key={`${entry.event.turn_index}-${entry.event.timestamp}`}
                        entry={entry}
                        index={index}
                        skipAnimation={index < liveActiveTurnIdx}
                        onComplete={index === liveActiveTurnIdx ? () => setLiveActiveTurnIdx((n) => n + 1) : undefined}
                        selected={selectedEntry?.event?.turn_index === entry.event.turn_index && drawerOpen}
                        onSelect={() => { setSelectedEntry(entry); setDrawerOpen(true); }}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="empty-card">
                    <div className="empty-card-heading">No turns yet</div>
                    <div className="empty-card-body">Once the backend completes the first turn, the timeline will appear here automatically.</div>
                  </div>
                )}

                {timeline.length && status?.status === "completed" ? (
                  <LiveBlueBenchmarkSection
                    key={`live-blue-results-${timeline.length}`}
                    timeline={timeline}
                  />
                ) : null}
              </>
            )}
          </div>
        ) : null}

        {activeView === "sandbox" ? (
          <div className="page-body">
            {activeSandboxRun ? (
              <SandboxView
                run={activeSandboxRun}
                onRunChange={updateSandboxRun}
                onCreateNewRun={createSandboxRun}
              />
            ) : (
              <div className="empty-state">
                <div className="empty-state-heading">No sandbox run active</div>
                <div className="empty-state-body">Create a sandbox run to begin submitting prompts.</div>
                <button type="button" className="btn btn-primary" onClick={createSandboxRun}>New sandbox run</button>
              </div>
            )}
          </div>
        ) : null}

        {activeView === "labs" ? (
          <div className="page-body">
            <LabsView
              labs={labs}
              onSave={saveLab}
              onDelete={deleteLab}
              onLaunch={launchLab}
            />
          </div>
        ) : null}

        {activeView === "evaluation" ? (
          <div className="page-body">
            <EvaluationView suiteRun={suiteRun} onStartSuite={startSuiteRun} onStopSuite={stopSuiteRun} onResetSuite={resetSuiteRun} loading={evalLoading} />
          </div>
        ) : null}
      </div>

      {wizardOpen ? (
        <SetupModal
          step={wizardStep}
          setup={setup}
          onField={updateField}
          onBack={handleWizardBack}
          onNext={() => setWizardStep((c) => Math.min(5, c + 1))}
          onLaunch={createRun}
          onClose={() => setWizardOpen(false)}
          loading={loading}
          hasRun={Boolean(runId)}
        />
      ) : null}
      {drawerOpen ? <TurnDrawer entry={selectedEntry} onClose={() => setDrawerOpen(false)} /> : null}
    </div>
  );
}
