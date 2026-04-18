import React from "react";
import { X, ShieldIcon } from "../../icons";
import { Badge, Pill } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import SandboxBlueTeamEvidence from "../sandbox/SandboxBlueTeamEvidence";
import {
  buildTurnBadgeLabels,
  getGateActionLabel,
  getGateActionTone,
  turnSummary,
  stageItems,
  formatLabel,
  formatNumber,
  truncateMiddle,
  toneForSeverity,
  toneForOutcome,
  toneForAction,
} from "../../utils/format";

export default function TurnDrawer({ entry, onClose }) {
  if (!entry) return null;
  const badgeLabels = buildTurnBadgeLabels(entry);
  const gateActionLabel = getGateActionLabel(entry.verdict);

  return (
    <div className="drawer-shell">
      <button type="button" className="drawer-backdrop" onClick={onClose} aria-label="Close drawer" />
      <aside className="drawer-panel">
        <div className="drawer-header">
          <div>
            <div className="drawer-title">Turn {entry.event.turn_index}</div>
            <div className="drawer-subtitle">{turnSummary(entry)}</div>
          </div>
          <button type="button" className="btn btn-ghost" style={{ padding: "0 6px" }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body">
          <div className="chip-row">
            <Pill tone={getGateActionTone(entry.verdict)}>{`Gate: ${gateActionLabel}`}</Pill>
            <Pill tone={toneForSeverity(entry.verdict.severity)}>{badgeLabels.severityShort}</Pill>
            <Pill tone={toneForOutcome(entry.event.outcome)}>{badgeLabels.objectiveShort}</Pill>
          </div>

          <div className="stage-strip">
            {stageItems(entry).map((item) => (
              <div className="stage-cell" key={item.label}>
                <div className="stage-cell-label">{item.label}</div>
                <div className="stage-cell-value">{item.value}</div>
              </div>
            ))}
          </div>

          <KeyGrid
            items={[
              { label: "Strategy", value: formatLabel(entry.event.strategy_id) },
              { label: "Template", value: formatLabel(entry.event.template_id) },
              { label: "Attack tag", value: formatLabel(entry.event.attack_tag) },
              { label: "Prompt hash", value: truncateMiddle(entry.event.prompt_hash) },
              { label: "Target", value: formatLabel(entry.event.target_provider) },
              { label: "Policy", value: truncateMiddle(entry.verdict.policy_id) },
            ]}
          />

          <Fold title="Attacker prompt" defaultOpen>
            <p className="micro-copy">Final prompt sent to the model (post-converter)</p>
            <DetailPre text={entry.event.input} />
          </Fold>

          <Fold title="Pre-converter prompt">
            <p className="micro-copy">Raw prompt from the attacker LLM, before converters were applied</p>
            <DetailPre text={entry.event.attacker_prompt} />
            {entry.event.attacker_rationale ? (
              <p className="micro-copy" style={{ marginTop: 12 }}>Rationale: {entry.event.attacker_rationale}</p>
            ) : null}
          </Fold>

          <Fold title="Converter steps">
            {entry.event.converter_steps?.length
              ? entry.event.converter_steps.map((step, index) => (
                  <div className="converter-card" key={`${step.name}-${index}`}>
                    <div className="converter-title">{formatLabel(step.name)}</div>
                    <DetailPre text={step.output} />
                  </div>
                ))
              : <p className="empty-copy">No converter steps recorded.</p>}
          </Fold>

          <Fold title="LLM output" defaultOpen>
            <DetailPre text={entry.event.model_output} />
            {entry.verdict.redacted_output ? (
              <Fold title="View redacted content">
                <p className="micro-copy" style={{ marginBottom: 8 }}>
                  Content intercepted and redacted by the blue-team guardrail.
                  In a deployed system this would not be visible to end users.
                </p>
                <DetailPre text={entry.verdict.redacted_output} />
              </Fold>
            ) : null}
          </Fold>

          <Fold title="Scorer verdict">
            <div className="score-panel">
              <div className="score-hero">
                <div className="score-hero-label">Objective LLM scorer</div>
                <div className="score-hero-value">{formatLabel(entry.event.objective_scorer?.label || "n/a")}</div>
                <div className="score-hero-note">{entry.event.objective_scorer?.reason || "No rationale recorded."}</div>
              </div>
              {entry.event.scorer_results?.map((scorer, index) => (
                <div className="score-row" key={`${scorer.name}-${index}`}>
                  <div>
                    <strong>{formatLabel(scorer.name)}</strong>
                    <div className="micro-copy">{scorer.reason}</div>
                  </div>
                  <div className="score-row-side">
                    <Pill tone={toneForOutcome(scorer.label)}>{formatLabel(scorer.label)}</Pill>
                    <span>{formatNumber(scorer.score)}</span>
                  </div>
                </div>
              ))}
            </div>
          </Fold>

          <Fold title="Blue-team evidence" defaultOpen>
            <SandboxBlueTeamEvidence verdict={entry.verdict} />

            <KeyGrid
              items={[
                { label: "Action",     value: gateActionLabel },
                { label: "Category",   value: formatLabel(entry.verdict.category) },
                { label: "Severity",   value: formatLabel(entry.verdict.severity) },
                { label: "Confidence", value: formatNumber(entry.verdict.confidence) },
                { label: "Dry run",    value: entry.verdict.dry_run ? "Yes — enforcement logged only" : "No" },
              ]}
            />

            <Fold title="Detector telemetry">
              <p className="micro-copy" style={{ marginBottom: 6, opacity: 0.55 }}>
                Raw detector_results payload as returned by the blue-team pipeline.
              </p>
              <DetailPre text={JSON.stringify(entry.verdict.detector_results || {}, null, 2)} />
            </Fold>
          </Fold>
        </div>{/* /drawer-body */}
      </aside>
    </div>
  );
}
