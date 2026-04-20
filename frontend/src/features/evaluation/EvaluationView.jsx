import React, { useState, useEffect, useMemo } from "react";
import StatCard from "../../components/StatCard";
import EvalBlueSummarySection from "./EvalBlueSummarySection";
import EvalInsightsSection from "./EvalInsightsSection";
import SuiteCaseRow from "./SuiteCaseRow";
import { SUITE_STORAGE_KEY } from "../../constants";
import { readStorageJSON, writeStorageJSON } from "../../utils/storage";
import { computeSuiteSummary } from "../../utils/analysis";
import { formatLabel, formatTimestamp } from "../../utils/format";

export default function EvaluationView({ suiteRun, onStartSuite, onStopSuite, onPauseSuite, onResumeSuite, onResetSuite, loading }) {
  const isRunning = suiteRun?.status === "running";
  const isPaused = suiteRun?.status === "paused";
  const isDone = suiteRun?.is_complete;
  const isCancelled = suiteRun?.status === "cancelled";
  const liveCases = suiteRun?.case_completed_results || [];

  function handleClear() {
    writeStorageJSON(SUITE_STORAGE_KEY, null);
    setSavedData(null);
    onResetSuite();
  }

  const [savedData, setSavedData] = useState(() =>
    readStorageJSON(SUITE_STORAGE_KEY, null)
  );

  useEffect(() => {
    if (suiteRun?.is_complete && liveCases.length > 0) {
      const toSave = {
        cases: liveCases,
        timestamp: new Date().toISOString(),
        provider: suiteRun.provider,
      };
      writeStorageJSON(SUITE_STORAGE_KEY, toSave);
      setSavedData(toSave);
    }
  }, [suiteRun?.is_complete, liveCases.length]);

  const cases = isRunning
    ? liveCases
    : liveCases.length > 0
    ? liveCases
    : savedData?.cases || [];
  const summary = useMemo(() => computeSuiteSummary(cases), [cases]);
  const isFromSave = liveCases.length === 0 && cases.length > 0;

  return (
    <section className="evaluation-page">
      <div className="section-header">
        <div>
          <div className="section-title">Attack Suite</div>
          <div className="section-note">Run automated red-team test cases against each scenario.</div>
        </div>
        <div className="chip-row">
          {isRunning ? (
            <>
              <button type="button" className="btn btn-secondary" onClick={onPauseSuite}>
                Pause
              </button>
              <button type="button" className="btn btn-danger" onClick={onStopSuite}>
                Stop run
              </button>
            </>
          ) : isPaused ? (
            <button type="button" className="btn btn-primary" onClick={onResumeSuite} disabled={loading}>
              Continue
            </button>
          ) : (
            <>
              {isDone && (
                <button type="button" className="btn btn-secondary" onClick={handleClear}>
                  Clear
                </button>
              )}
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => onStartSuite("groq")}
                disabled={loading}
              >
                {isDone ? "New run" : "Run attack suite"}
              </button>
            </>
          )}
        </div>
      </div>

      {isRunning && (
        <div className="suite-progress-banner">
          <div className="suite-progress-top">
            <span className="suite-progress-label">
              Case {suiteRun.completed_cases} of {suiteRun.total_cases}
            </span>
            <span className="suite-progress-pct">{suiteRun.progress_percentage}%</span>
          </div>
          <div className="suite-progress-bar">
            <div className="suite-progress-fill" style={{ width: `${suiteRun.progress_percentage}%` }} />
          </div>
          {suiteRun.current_case_id && (
            <div className="suite-progress-current">{suiteRun.current_case_id}</div>
          )}
        </div>
      )}

      {isPaused && (
        <div className="suite-progress-banner suite-paused-banner">
          <div className="suite-progress-top">
            <span className="suite-progress-label">
              Paused · {suiteRun.completed_cases} of {suiteRun.total_cases} cases completed
            </span>
            <button type="button" className="btn btn-primary" onClick={onResumeSuite} disabled={loading}>
              Continue
            </button>
          </div>
          <div className="suite-progress-bar">
            <div className="suite-progress-fill" style={{ width: `${suiteRun.progress_percentage}%` }} />
          </div>
          <div className="suite-progress-current">Rate limit reached — click Continue to resume</div>
        </div>
      )}

      {summary && !isRunning && (
        <>
          {isCancelled && (
            <div className="suite-saved-note">
              Run stopped · {suiteRun.completed_cases} of {suiteRun.total_cases} cases completed
            </div>
          )}
          {!isCancelled && isFromSave && savedData?.timestamp && (
            <div className="suite-saved-note">
              Last run · {formatTimestamp(savedData.timestamp)}
              {savedData.provider ? ` · ${formatLabel(savedData.provider)}` : ""}
            </div>
          )}
          <div className="stat-bar">
            <StatCard label="Cases" value={summary.total} />
            <StatCard label="Breached" value={summary.succeeded} />
            <StatCard label="Defended" value={summary.defended} />
            <StatCard label="Guardrail fires" value={summary.guardrailFired} />
            <StatCard label="Avg turns" value={summary.avgTurns} />
          </div>
          <EvalInsightsSection cases={cases} />
          <EvalBlueSummarySection cases={cases} />
        </>
      )}

      {cases.length > 0 ? (
        <div className="suite-case-list">
          {cases.map((c, idx) => (
            <SuiteCaseRow key={c.case_id || idx} caseData={c} index={idx} />
          ))}
        </div>
      ) : !isRunning ? (
        <div className="empty-state">
          <p className="empty-copy">No results yet. Run the attack suite to see test cases appear here.</p>
        </div>
      ) : null}
    </section>
  );
}
