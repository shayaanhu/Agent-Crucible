import React from "react";
import { X, ShieldIcon, Bot, Sword } from "../../icons";
import { Pill } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import SandboxBlueTeamEvidence from "./SandboxBlueTeamEvidence";
import {
  toneForAction,
  toneForSeverity,
  formatLabel,
  formatNumber,
  formatTimestamp,
  truncateMiddle,
} from "../../utils/format";

export default function SandboxTurnDrawer({ turn, index, onClose }) {
  if (!turn) return null;

  const verdict = turn.verdict || {};
  const action = verdict.action || "allow";
  const severity = verdict.severity || "low";

  return (
    <div className="drawer-shell">
      <button type="button" className="drawer-backdrop" onClick={onClose} aria-label="Close drawer" />
      <aside className="drawer-panel">
        <div className="drawer-header">
          <div>
            <div className="drawer-title">Turn {index + 1} · Sandbox</div>
            <div className="drawer-subtitle">
              {verdict.reason || "Blue-team evaluation complete."}
            </div>
          </div>
          <button type="button" className="btn btn-ghost" style={{ padding: "0 6px" }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body">
          {/* Quick-glance chip row */}
          <div className="chip-row">
            <Pill tone={toneForAction(action)}>Gate: {formatLabel(action)}</Pill>
            <Pill tone={toneForSeverity(severity)}>Sev: {formatLabel(severity)}</Pill>
            {turn.detection_latency_ms != null && (
              <Pill tone="neutral">{turn.detection_latency_ms}ms</Pill>
            )}
          </div>

          {/* Key metadata row */}
          <KeyGrid
            items={[
              { label: "Action", value: formatLabel(action) },
              { label: "Severity", value: formatLabel(severity) },
              { label: "Confidence", value: formatNumber(verdict.confidence) },
              { label: "Category", value: formatLabel(verdict.category) },
              { label: "Policy", value: truncateMiddle(verdict.policy_id) },
              { label: "Timestamp", value: formatTimestamp(turn.timestamp) },
            ]}
          />

          {/* User's prompt */}
          <Fold title="Your prompt" defaultOpen>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
              <Sword size={12} strokeWidth={1.5} style={{ color: "var(--text-tertiary)", flexShrink: 0 }} />
              <span className="micro-copy">What you sent to the model</span>
            </div>
            <DetailPre text={turn.prompt} />
          </Fold>

          {/* LLM response */}
          <Fold title="LLM output" defaultOpen>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
              <Bot size={12} strokeWidth={1.5} style={{ color: "var(--text-tertiary)", flexShrink: 0 }} />
              <span className="micro-copy">Model response</span>
            </div>
            <DetailPre text={turn.response} />
          </Fold>

          {/* Blue-team evidence — full breakdown */}
          <Fold title="Blue-team evidence" defaultOpen>
            <SandboxBlueTeamEvidence verdict={verdict} />
          </Fold>
        </div>
      </aside>
    </div>
  );
}
