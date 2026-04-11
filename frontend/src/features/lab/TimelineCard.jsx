import React, { useState, useEffect } from "react";
import { Sword, ShieldIcon, Bot, ChevronRight } from "../../icons";
import { Badge } from "../../components/Badge";
import TypewriterText from "../../components/TypewriterText";
import {
  buildTurnBadgeLabels,
  getGateActionLabel,
  getGateActionTone,
  previewText,
  formatLabel,
  formatTimestamp,
  toneForSeverity,
  toneForOutcome,
} from "../../utils/format";

export default function TimelineCard({ entry, selected, onSelect, index }) {
  const severity = entry.verdict?.severity || "low";
  const badgeLabels = buildTurnBadgeLabels(entry);
  const blueAction = getGateActionLabel(entry.verdict);
  const blueSeverity = formatLabel(entry.verdict?.severity || "low");
  const converterCount = entry.event.converter_steps?.length || 0;
  const attackerPreview = previewText(entry.event.input, 210);
  const targetPreview = previewText(entry.event.model_output, 230);

  // 0: attacker typing  1: attacker done → waiting → gate  2: gate visible → waiting → target  3: target visible
  const [phase, setPhase] = useState(0);
  useEffect(() => {
    if (phase === 1) {
      const t = setTimeout(() => setPhase(2), 350);
      return () => clearTimeout(t);
    }
    if (phase === 2) {
      const t = setTimeout(() => setPhase(3), 630); // gate anim (380ms) + gap (250ms)
      return () => clearTimeout(t);
    }
  }, [phase]);

  return (
    <div
      role="button"
      tabIndex={0}
      className={`turn-row severity-${severity}${selected ? " is-selected" : ""}`}
      style={{ animationDelay: `${(index || 0) * 60}ms` }}
      onClick={onSelect}
      onKeyDown={(e) => e.key === "Enter" && onSelect()}
    >
      {/* Timeline node */}
      <div className="turn-node-col">
        <div className="turn-node-circle" style={{ animationDelay: `${(index || 0) * 60 + 40}ms` }} />
      </div>

      <div className="turn-row-body">
        {/* Header row: turn number + badges */}
        <div className="turn-row-top">
          <div>
            <div className="turn-number">Turn {entry.event.turn_index}</div>
            <div className="turn-meta">{formatLabel(entry.event.strategy_id)} · {formatTimestamp(entry.event.timestamp)}</div>
          </div>
          <div className="turn-badges">
            <span title={badgeLabels.severityLong}>
              <Badge tone={toneForSeverity(severity)}>{badgeLabels.severityShort}</Badge>
            </span>
            <span title={badgeLabels.objectiveLong}>
              <Badge tone={toneForOutcome(entry.event.outcome)}>{badgeLabels.objectiveShort}</Badge>
            </span>
          </div>
        </div>

        {/* Conversation blocks — phase-gated: attacker types → gate fades in → target types */}
        <div className="turn-exchange">
          <div className="turn-speaker-block attacker" style={{ animation: "blockIn 380ms var(--ease-out) 150ms both" }}>
            <div className="turn-speaker-icon attacker"><Sword size={13} strokeWidth={1.5} /></div>
            <div className={`turn-speaker-text${attackerPreview.truncated ? " is-truncated" : ""}`}>
              <TypewriterText text={attackerPreview.text} speed={12} delay={150} onDone={() => setPhase(1)} />
            </div>
          </div>
          {phase >= 2 && (
            <div className="turn-gate" style={{ animation: "blockIn 380ms var(--ease-out) both" }}>
              <div className="turn-gate-left">
                <ShieldIcon size={14} strokeWidth={1.7} />
                <span className="turn-gate-label">Blue-team checkpoint</span>
              </div>
              <div className="turn-gate-status">
                <span className={`gate-pill gate-pill-${getGateActionTone(entry.verdict)}`}>{blueAction}</span>
                <span className={`gate-pill gate-pill-${toneForSeverity(entry.verdict?.severity)}`}>{blueSeverity}</span>
              </div>
            </div>
          )}
          {phase >= 3 && (
            <div className="turn-speaker-block target" style={{ animation: "blockIn 380ms var(--ease-out) both" }}>
              <div className="turn-speaker-icon target"><Bot size={13} strokeWidth={1.5} /></div>
              <div className={`turn-speaker-text${targetPreview.truncated ? " is-truncated" : ""}`}>
                <TypewriterText text={targetPreview.text} speed={12} />
              </div>
            </div>
          )}
        </div>

        {/* Expand affordance row */}
        <div className="turn-expand-row">
          {converterCount > 0 && (
            <button type="button" className="turn-expand-trigger" onClick={(e) => { e.stopPropagation(); onSelect(); }}>
              <ChevronRight size={11} /> Converter steps ({converterCount})
            </button>
          )}
          <button type="button" className="turn-expand-trigger" onClick={(e) => { e.stopPropagation(); onSelect(); }}>
            <ChevronRight size={11} /> Scorer detail
          </button>
          <button type="button" className="turn-expand-trigger" onClick={(e) => { e.stopPropagation(); onSelect(); }}>
            <ChevronRight size={11} /> Blue-team evidence
          </button>
        </div>
      </div>
    </div>
  );
}
