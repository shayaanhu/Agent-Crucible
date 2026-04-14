import React, { useState } from "react";
import { ChevronDown, PlayCircle, Pencil, Trash2 } from "../../icons";
import { Badge } from "../../components/Badge";
import { formatLabel } from "../../utils/format";
import { SUCCESS_CRITERIA_OPTIONS } from "../../constants";

function toneForDifficulty(d) {
  if (d === "beginner") return "safe";
  if (d === "intermediate") return "warning";
  if (d === "advanced") return "danger";
  return "neutral";
}

export default function LabCard({ lab, index, onLaunch, onEdit, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const criteriaLabel = SUCCESS_CRITERIA_OPTIONS.find((o) => o.value === lab.success_criteria)?.label || lab.success_criteria;

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
          <Badge tone={toneForDifficulty(lab.difficulty)}>{formatLabel(lab.difficulty)}</Badge>
          <span className="suite-case-goal">{lab.title}</span>
        </div>
        <div className="suite-case-right">
          <span className="suite-case-chip">{lab.estimated_minutes} min</span>
          <span className="suite-case-chip suite-case-chip-dim">{formatLabel(lab.pre_config?.strategy_id)}</span>
          <span className="suite-case-chip suite-case-chip-dim">{lab.pre_config?.scenario}</span>
          <ChevronDown
            size={13}
            strokeWidth={2}
            className={`suite-case-chevron${expanded ? " is-open" : ""}`}
          />
        </div>
      </button>

      {expanded && (
        <div className="suite-case-body">
          <div className="lab-card-body">
            <div className="lab-objective-block">
              <div className="lab-objective-label">Learning objective</div>
              <div className="lab-objective-text">{lab.learning_objective}</div>
            </div>

            {lab.description && (
              <div className="lab-description">{lab.description}</div>
            )}

            <div className="eval-grid" style={{ marginTop: 12 }}>
              <section className="eval-section">
                <div className="eval-section-title">Attack configuration</div>
                <div className="insights-coverage-list">
                  <div className="insights-coverage-row">
                    <span className="insights-coverage-label">Scenario</span>
                    <span className="lab-config-value">{lab.pre_config?.scenario}</span>
                  </div>
                  <div className="insights-coverage-row">
                    <span className="insights-coverage-label">Strategy</span>
                    <span className="lab-config-value">{formatLabel(lab.pre_config?.strategy_id)}</span>
                  </div>
                  <div className="insights-coverage-row">
                    <span className="insights-coverage-label">Max turns</span>
                    <span className="lab-config-value">{lab.pre_config?.max_turns}</span>
                  </div>
                  <div className="insights-coverage-row">
                    <span className="insights-coverage-label">Dry run</span>
                    <span className="lab-config-value">{lab.pre_config?.dry_run ? "Yes" : "No"}</span>
                  </div>
                </div>
              </section>

              <section className="eval-section">
                <div className="eval-section-title">Success criteria</div>
                <div className="lab-criteria-text">{criteriaLabel}</div>
                {lab.reflection && (
                  <>
                    <div className="eval-section-title" style={{ marginTop: 12 }}>Reflection</div>
                    <div className="lab-reflection-text">{lab.reflection}</div>
                  </>
                )}
              </section>
            </div>

            <div className="lab-card-actions">
              <button type="button" className="btn btn-primary" onClick={() => onLaunch(lab)}>
                <PlayCircle size={13} strokeWidth={1.5} />
                Launch lab
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => onEdit(lab)}>
                <Pencil size={13} strokeWidth={1.5} />
                Edit
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => onDelete(lab.id)}>
                <Trash2 size={13} strokeWidth={1.5} />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
