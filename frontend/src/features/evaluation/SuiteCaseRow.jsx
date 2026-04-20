import React, { useState } from "react";
import { ChevronDown } from "../../icons";
import { Badge } from "../../components/Badge";
import SandboxTurnCard from "../sandbox/SandboxTurnCard";
import {
  toneForOutcome,
  labelForOutcome,
  formatLabel,
} from "../../utils/format";

export default function SuiteCaseRow({ caseData, index }) {
  const [expanded, setExpanded] = useState(false);
  const [activeTurnIdx, setActiveTurnIdx] = useState(0);
  const outcome = caseData.final_outcome || "no_success";
  const turns = caseData.turns || [];
  const blueBlocked = caseData.blue_team_any_blocked;
  const outcomeTone = toneForOutcome(outcome);

  return (
    <div
      className={`suite-case-row${expanded ? " is-expanded" : ""}`}
      style={{ animationDelay: `${index * 40}ms` }}
    >
      <button
        type="button"
        className="suite-case-header"
        onClick={() => setExpanded((e) => !e)}
      >
        <div className="suite-case-left">
          <Badge tone={outcomeTone}>{labelForOutcome(outcome)}</Badge>
          <span className="suite-case-goal">{caseData.goal || caseData.case_id}</span>
        </div>
        <div className="suite-case-right">
          {caseData.scenario && <span className="suite-case-chip">{caseData.scenario}</span>}
          {caseData.strategy_id && (
            <span className="suite-case-chip suite-case-chip-dim">{formatLabel(caseData.strategy_id)}</span>
          )}
          {caseData.difficulty && (
            <span className="suite-case-chip suite-case-chip-dim">{formatLabel(caseData.difficulty)}</span>
          )}
          {blueBlocked && <Badge tone="info">Guardrail fired</Badge>}
          <span className="suite-case-turns">
            {turns.length} turn{turns.length !== 1 ? "s" : ""}
          </span>
          <ChevronDown
            size={13}
            strokeWidth={2}
            className={`suite-case-chevron${expanded ? " is-open" : ""}`}
          />
        </div>
      </button>

      {expanded && (
        <div className="suite-case-body">
          <div className="timeline-list">
            {turns.slice(0, activeTurnIdx + 1).map((turn, tIdx) => {
              const blueVerdict = caseData.blue_team_verdicts?.find(
                (v) => v.turn_index === turn.turn_index
              );
              const fallbackVerdict = turn.response
                ? {
                    allowed: true,
                    action: "allow",
                    severity: "low",
                    category: "n/a",
                    confidence: null,
                    policy_id: "",
                  }
                : null;
              const verdict = blueVerdict || fallbackVerdict;
              const isActive = tIdx === activeTurnIdx;
              return (
                <SandboxTurnCard
                  key={`${caseData.case_id || "case"}-${turn.turn_index || tIdx + 1}`}
                  index={tIdx}
                  skipAnimation={!isActive}
                  onComplete={isActive ? () => setActiveTurnIdx((i) => i + 1) : undefined}
                  turn={{
                    id: `${caseData.case_id || "case"}-${turn.turn_index || tIdx + 1}`,
                    prompt: turn.attacker_prompt || turn.prompt || "",
                    response: turn.response || "",
                    verdict,
                    isPending: !verdict,
                    detection_latency_ms: turn.detection_latency_ms,
                    timestamp: turn.timestamp || caseData.timestamp,
                  }}
                />
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
