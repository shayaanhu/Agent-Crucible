import React from "react";
import { Badge } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import { formatLabel, formatNumber } from "../../utils/format";

export default function SandboxBlueTeamEvidence({ verdict }) {
  if (!verdict) return null;
  const dr = verdict.detector_results || {};
  const decision = dr._decision || {};
  const aggregation = dr._aggregation || {};
  const detectorEntries = Object.entries(dr).filter(([k]) => !k.startsWith("_"));
  const policyEvals = aggregation.policy_evaluations || [];

  return (
    <div style={{ display: "grid", gap: 14 }}>
      <KeyGrid
        items={[
          { label: "Outcome",     value: decision.outcome === "unsafe" ? "Unsafe" : "Safe" },
          { label: "Action",      value: formatLabel(verdict.action) },
          { label: "Category",    value: formatLabel(verdict.category) },
          { label: "Severity",    value: formatLabel(verdict.severity) },
          { label: "Confidence",  value: formatNumber(verdict.confidence) },
          { label: "Policy",      value: verdict.policy_id },
          { label: "Aggregation", value: formatLabel(decision.aggregation_strategy) },
          { label: "Supporting",  value: (decision.supporting_detectors || []).join(", ") || "none" },
        ]}
      />
      {decision.rationale && (
        <>
          <p className="micro-copy">Rationale</p>
          <DetailPre text={decision.rationale} />
        </>
      )}

      {detectorEntries.length > 0 && (
        <div>
          <p className="micro-copy" style={{ marginBottom: 8 }}>Detector breakdown</p>
          {detectorEntries.map(([name, result]) => {
            const signals = result.signals || [];
            const matched = result.matched_patterns || [];
            const flagged = signals.some((s) => s.flagged);
            return (
              <div key={name} className="sandbox-detector-card">
                <div className="sandbox-detector-header">
                  <span className="sandbox-detector-name">{formatLabel(name)}</span>
                  <Badge tone={flagged ? "danger" : "safe"}>{flagged ? "Flagged" : "Clean"}</Badge>
                </div>
                {matched.length > 0 && (
                  <div className="sandbox-detector-patterns">
                    <p className="micro-copy" style={{ marginBottom: 4 }}>Matched patterns</p>
                    {matched.map((p, i) => (
                      <code key={i} className="sandbox-pattern-chip">{p}</code>
                    ))}
                  </div>
                )}
                {signals.map((sig, i) => (
                  <div key={i} className="sandbox-signal-row">
                    <span className="micro-copy" style={{ color: "var(--text-primary)", flex: 1 }}>
                      {sig.policy_id
                        ? sig.policy_id.replace(/^policy\./, "").replace(/\./g, " › ")
                        : "signal"}
                    </span>
                    <span className="micro-copy">conf: {formatNumber(sig.confidence)}</span>
                    <Badge tone={sig.flagged ? "danger" : "neutral"}>
                      {sig.flagged ? "Flagged" : "Not flagged"}
                    </Badge>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}

      {policyEvals.length > 0 && (
        <Fold title="Policy evaluation log">
          <div style={{ display: "grid", gap: 4 }}>
            {policyEvals.map((ev) => (
              <div key={ev.policy_id} className="sandbox-policy-row">
                <span className="sandbox-policy-id">{ev.policy_id}</span>
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <span className="micro-copy">conf: {formatNumber(ev.aggregated_confidence)}</span>
                  <Badge tone={ev.triggered ? "danger" : "neutral"}>
                    {ev.triggered ? "Triggered" : "Not triggered"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Fold>
      )}
    </div>
  );
}
