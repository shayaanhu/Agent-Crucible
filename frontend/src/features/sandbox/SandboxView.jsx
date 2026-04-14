import React, { useState, useEffect, useRef, useMemo } from "react";
import { PlayCircle } from "../../icons";
import SectionHeader from "../../components/SectionHeader";
import SandboxTurnCard from "./SandboxTurnCard";
import SandboxTurnDrawer from "./SandboxTurnDrawer";
import { API_BASE } from "../../constants";
import { isEmpty, toneForSeverity } from "../../utils/format";

const MAX_TURNS = 10;

export default function SandboxView({ run, onRunChange, onCreateNewRun }) {
  const [turns, setTurns] = useState(() =>
    Array.isArray(run?.turns) ? run.turns.filter((t) => !t?.isPending) : []
  );
  const [currentPrompt, setCurrentPrompt] = useState(() =>
    typeof run?.currentPrompt === "string" ? run.currentPrompt : ""
  );
  const [activeTurnIdx, setActiveTurnIdx] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState("");
  const [selectedTurn, setSelectedTurn] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const textareaRef = useRef(null);
  const completedTurns = useMemo(() => turns.filter((t) => !t.isPending && t.verdict), [turns]);

  useEffect(() => {
    setTurns(Array.isArray(run?.turns) ? run.turns.filter((t) => !t?.isPending) : []);
    setCurrentPrompt(typeof run?.currentPrompt === "string" ? run.currentPrompt : "");
    setActiveTurnIdx(0);
    setError("");
    setIsRunning(false);
    setDrawerOpen(false);
    setSelectedTurn(null);
  }, [run?.id]);

  useEffect(() => {
    if (!run?.id) return;
    onRunChange?.(run.id, { turns, currentPrompt });
  }, [run?.id, turns, currentPrompt]);

  const blueTeamSummary = useMemo(() => {
    if (!completedTurns.length) return { blocked: 0, highestSeverity: "n/a" };
    const blocked = completedTurns.filter((t) => !t.verdict?.allowed).length;
    const order = ["critical", "high", "medium", "low"];
    const highest = completedTurns.reduce((best, t) => {
      const s = t.verdict?.severity || "low";
      return order.indexOf(s) < order.indexOf(best) ? s : best;
    }, "low");
    return { blocked, highestSeverity: highest };
  }, [completedTurns]);

  async function handleSubmit() {
    if (!currentPrompt.trim() || isRunning || turns.length >= MAX_TURNS) return;
    const turnId =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `turn-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const promptText = currentPrompt.trim();
    setError("");
    setIsRunning(true);
    setCurrentPrompt("");
    setTurns((prev) => [
      ...prev,
      {
        id: turnId,
        prompt: promptText,
        response: "",
        verdict: null,
        isPending: true,
        timestamp: new Date().toISOString(),
      },
    ]);
    try {
      const history = turns
        .filter((t) => !t.isPending && !isEmpty(t.response))
        .flatMap((t) => [
          { role: "user", content: t.prompt },
          { role: "assistant", content: t.response },
        ]);
      const resp = await fetch(`${API_BASE}/api/v1/sandbox/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: promptText, scenario: "", provider: "groq", history }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || "Run failed");
      setTurns((prev) =>
        prev.map((turn) => {
          if (turn.id !== turnId) return turn;
          return {
            ...turn,
            response: data.response,
            verdict: data.verdict,
            detection_latency_ms: data.detection_latency_ms,
            timestamp: data.timestamp || turn.timestamp,
            isPending: false,
          };
        })
      );
    } catch (e) {
      setTurns((prev) => prev.filter((turn) => turn.id !== turnId));
      setError(e.message);
      setCurrentPrompt(promptText);
    } finally {
      setIsRunning(false);
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  }

  function handleReset() {
    setTurns([]);
    setCurrentPrompt("");
    setError("");
    setTimeout(() => textareaRef.current?.focus(), 100);
  }

  function handleNewRun() {
    if (onCreateNewRun) {
      onCreateNewRun();
      return;
    }
    handleReset();
  }

  const canSubmit = Boolean(currentPrompt.trim()) && !isRunning && turns.length < MAX_TURNS;
  const reachedMax = turns.length >= MAX_TURNS;

  return (
    <section>
      <SectionHeader
        title="Attack Sandbox"
        note="Write your own attack prompts turn by turn — up to 10 turns. See exactly how the blue-team guardrails evaluated each one."
      />

      {turns.length > 0 && (
        <>
          <div className="stat-bar">
            <div className="stat-cell">
              <div className="stat-cell-label">Turns</div>
              <div className="stat-cell-value">{turns.length} / {MAX_TURNS}</div>
            </div>
            <div className="stat-cell">
              <div className="stat-cell-label">Blue-team blocked</div>
              <div className={`stat-cell-value${blueTeamSummary.blocked > 0 ? " val-danger" : ""}`}>
                {blueTeamSummary.blocked}
              </div>
            </div>
            <div className="stat-cell">
              <div className="stat-cell-label">Highest severity</div>
              <div className={`stat-cell-value val-${toneForSeverity(blueTeamSummary.highestSeverity)}`}>
                {blueTeamSummary.highestSeverity}
              </div>
            </div>
            <div className="stat-cell" style={{ marginLeft: "auto" }}>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ fontSize: "0.75rem", padding: "4px 10px" }}
                onClick={handleNewRun}
              >
                New sandbox run
              </button>
            </div>
          </div>
          <div
            className="timeline-outcome-bar"
            style={{
              "--outcome-color":
                completedTurns.length === 0
                  ? "var(--neutral)"
                  : blueTeamSummary.blocked > 0
                  ? "var(--success)"
                  : blueTeamSummary.highestSeverity === "critical"
                  ? "var(--danger)"
                  : blueTeamSummary.highestSeverity === "high"
                  ? "var(--warning)"
                  : "var(--info)",
            }}
          />
        </>
      )}

      <div className="section-header">
        <div className="section-title">Turn timeline</div>
      </div>

      {turns.length === 0 && !isRunning ? (
        <div className="empty-card">
          <div className="empty-card-heading">No turns yet</div>
          <div className="empty-card-body">Write your first attack prompt below and submit to start the session.</div>
        </div>
      ) : (
        <div className="timeline-list">
          {turns.slice(0, activeTurnIdx + 1).map((turn, i) => (
            <SandboxTurnCard
              key={turn.id || i}
              turn={turn}
              index={i}
              skipAnimation={i < activeTurnIdx}
              onComplete={i === activeTurnIdx ? () => setActiveTurnIdx((n) => n + 1) : undefined}
              selected={drawerOpen && selectedTurn?.id === turn.id}
              onSelect={() => { setSelectedTurn(turn); setDrawerOpen(true); }}
            />
          ))}
        </div>
      )}

      {error ? <div className="error-banner" style={{ margin: "12px 0" }}>{error}</div> : null}

      <div className="sandbox-compose" style={{ marginTop: 20 }}>
        {reachedMax ? (
          <div style={{ textAlign: "center", padding: "8px 0" }}>
            <div className="empty-card-heading">Maximum turns reached</div>
            <div className="empty-card-body" style={{ marginBottom: 14 }}>
              Session complete — {MAX_TURNS} turns.
            </div>
            <button type="button" className="btn btn-primary" onClick={handleNewRun}>
              New sandbox run
            </button>
          </div>
        ) : (
          <>
            <div>
              <label className="field-label">Turn {turns.length + 1} · Attack prompt</label>
              <textarea
                ref={textareaRef}
                className="sandbox-textarea"
                value={currentPrompt}
                onChange={(e) => setCurrentPrompt(e.target.value)}
                placeholder={
                  turns.length === 0
                    ? "Write your first attack prompt. Try to get the model to bypass its guardrails."
                    : "Write your next prompt. Build on what you've learned from previous turns."
                }
                onKeyDown={(e) => {
                  if (
                    e.key === "Enter" &&
                    !e.shiftKey &&
                    !e.ctrlKey &&
                    !e.metaKey &&
                    !e.altKey
                  ) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                disabled={isRunning}
              />
              <div className="field-hint">Enter to submit · Shift + Enter for newline</div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button
                type="button"
                className="btn btn-primary"
                disabled={!canSubmit}
                onClick={handleSubmit}
              >
                <PlayCircle size={14} />
                {isRunning ? "Running…" : `Submit turn ${turns.length + 1}`}
              </button>
            </div>
          </>
        )}
      </div>
      {drawerOpen && selectedTurn && (
        <SandboxTurnDrawer
          turn={selectedTurn}
          index={turns.findIndex((t) => t.id === selectedTurn.id)}
          onClose={() => setDrawerOpen(false)}
        />
      )}
    </section>
  );
}
