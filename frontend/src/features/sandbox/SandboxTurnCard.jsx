import React, { useState, useEffect, useRef } from "react";
import { Sword, ShieldIcon, Bot } from "../../icons";
import { Badge } from "../../components/Badge";
import TypewriterText from "../../components/TypewriterText";
import Fold from "../../components/Fold";
import SandboxBlueTeamEvidence from "./SandboxBlueTeamEvidence";
import {
  toneForSeverity,
  toneForAction,
  formatLabel,
  formatTimestamp,
} from "../../utils/format";

export default function SandboxTurnCard({ turn, index, onSelect, selected, skipAnimation = false, onComplete }) {
  const isPending = Boolean(turn.isPending || !turn.verdict);
  const severity = turn.verdict?.severity || "low";
  const action = turn.verdict?.action || "allow";
  const [phase, setPhase] = useState(skipAnimation ? 3 : 0);
  const onCompleteRef = useRef(onComplete);
  useEffect(() => { onCompleteRef.current = onComplete; });

  useEffect(() => {
    if (isPending) return;
    if (phase === 1) {
      const t = setTimeout(() => setPhase(2), 350);
      return () => clearTimeout(t);
    }
    if (phase === 2) {
      const t = setTimeout(() => setPhase(3), 630);
      return () => clearTimeout(t);
    }
    if (phase === 3 && !skipAnimation) {
      const t = setTimeout(() => onCompleteRef.current?.(), 500);
      return () => clearTimeout(t);
    }
  }, [phase, isPending, skipAnimation]);

  return (
    <div
      role={isPending ? undefined : "button"}
      tabIndex={isPending ? undefined : 0}
      className={`turn-row${isPending ? "" : ` severity-${severity}`}${selected ? " is-selected" : ""}${isPending ? "" : " is-clickable"}`}
      style={{ animationDelay: `${index * 60}ms`, cursor: isPending ? "default" : "pointer" }}
      onClick={isPending ? undefined : onSelect}
      onKeyDown={isPending ? undefined : (e) => e.key === "Enter" && onSelect?.()}
    >
      <div className="turn-node-col">
        <div className="turn-node-circle" style={{ animationDelay: `${index * 60 + 40}ms` }} />
      </div>
      <div className="turn-row-body">
        <div className="turn-row-top">
          <div>
            <div className="turn-number">Turn {index + 1}</div>
            <div className="turn-meta">
              {turn.detection_latency_ms != null ? `${turn.detection_latency_ms}ms detection · ` : ""}
              {formatTimestamp(turn.timestamp)}
            </div>
          </div>
          <div className="turn-badges">
            {isPending ? (
              <Badge tone="neutral">Pending</Badge>
            ) : (
              <>
                <Badge tone={toneForSeverity(severity)}>{formatLabel(severity)}</Badge>
                <Badge tone={toneForAction(action)}>{formatLabel(action)}</Badge>
              </>
            )}
          </div>
        </div>

        <div className="turn-exchange">
          <div
            className="turn-speaker-block attacker"
            style={{ animation: "blockIn 380ms var(--ease-out) 150ms both" }}
          >
            <div className="turn-speaker-icon attacker"><Sword size={13} strokeWidth={1.5} /></div>
            <div className="turn-speaker-text">
              <TypewriterText text={turn.prompt} speed={12} delay={150} skip={skipAnimation} onDone={skipAnimation ? undefined : () => setPhase(1)} />
            </div>
          </div>
          {!isPending && phase >= 2 && (
            <div className="turn-gate" style={{ animation: "blockIn 380ms var(--ease-out) both" }}>
              <div className="turn-gate-left">
                <ShieldIcon size={14} strokeWidth={1.7} />
                <span className="turn-gate-label">Blue-team checkpoint</span>
              </div>
              <div className="turn-gate-status">
                <span className={`gate-pill gate-pill-${toneForAction(action)}`}>{formatLabel(action)}</span>
                <span className={`gate-pill gate-pill-${toneForSeverity(severity)}`}>{formatLabel(severity)}</span>
              </div>
            </div>
          )}
          {!isPending && phase >= 3 && (
            <div
              className="turn-speaker-block target"
              style={{ animation: "blockIn 380ms var(--ease-out) both" }}
            >
              <div className="turn-speaker-icon target"><Bot size={13} strokeWidth={1.5} /></div>
              <div className="turn-speaker-text">{turn.response}</div>
            </div>
          )}
        </div>

        {!isPending && phase >= 3 && (
          <Fold title="Blue-team evidence">
            <SandboxBlueTeamEvidence verdict={turn.verdict} />
          </Fold>
        )}
      </div>
    </div>
  );
}
