import React, { useState } from "react";
import { ArrowLeft, X, Check } from "../../icons";
import {
  SCENARIO_CARDS,
  SCENARIO_GOALS,
  PROVIDER_OPTIONS,
  MODEL_OPTIONS,
  STRATEGY_OPTIONS,
  DIFFICULTY_OPTIONS,
  SUCCESS_CRITERIA_OPTIONS,
  PRESET_PLACEHOLDER,
} from "../../constants";
import { formatLabel, selectState } from "../../utils/format";
import TurnsStepper from "../lab/TurnsStepper";

const TOTAL_STEPS = 5;

function generateId() {
  return typeof crypto !== "undefined" && crypto.randomUUID
    ? `lab-${crypto.randomUUID()}`
    : `lab-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function blank() {
  return {
    id: generateId(),
    title: "",
    difficulty: "beginner",
    estimated_minutes: 10,
    learning_objective: "",
    description: "",
    success_criteria: "any_success",
    reflection: "",
    pre_config: {
      scenario: "",
      goal: "",
      strategy_id: "direct_jailbreak",
      provider: "groq",
      attacker_model: "gpt-oss-120b",
      target_model: "llama-3.1-8b-instant",
      max_turns: 3,
      dry_run: false,
    },
    created_at: new Date().toISOString(),
  };
}

export default function LabCreateModal({ initialLab, onSave, onClose }) {
  const [step, setStep] = useState(1);
  const [draft, setDraft] = useState(() =>
    initialLab
      ? { ...initialLab, pre_config: { ...initialLab.pre_config } }
      : blank()
  );

  function setField(key, value) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  function setConfigField(key, value) {
    setDraft((d) => ({
      ...d,
      pre_config: { ...d.pre_config, [key]: value },
    }));
  }

  const goalSelectValue = selectState(
    draft.pre_config.goal,
    SCENARIO_GOALS[draft.pre_config.scenario] || []
  );

  const canAdvance =
    step === 1 ? Boolean(draft.title.trim()) :
    step === 2 ? Boolean(draft.learning_objective.trim()) :
    step === 3 ? Boolean(draft.pre_config.scenario) :
    step === 4 ? Boolean(draft.pre_config.goal.trim()) :
    true;

  return (
    <div className="modal-shell">
      <div className="modal-backdrop" onClick={onClose} />
      <section className="modal-card">
        <button
          type="button"
          className="btn btn-ghost"
          style={{ position: "absolute", top: 16, right: 16, padding: "0 6px" }}
          onClick={onClose}
        >
          <X size={16} />
        </button>

        <div className="step-indicator">
          <span className="step-counter">Step {step} of {TOTAL_STEPS}</span>
          <div className="step-dots">
            {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((n) => (
              <div
                key={n}
                className={`step-dot${n < step ? " is-done" : n === step ? " is-active" : ""}`}
              />
            ))}
          </div>
        </div>

        {/* Step 1 — Lab identity */}
        {step === 1 && (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Name your lab</div>
              <div className="wizard-subtitle">Give this lab a title, difficulty, and estimated time.</div>
            </div>
            <div className="wizard-body attack-form">
              <div>
                <label className="field-label">Title</label>
                <input
                  className="input"
                  type="text"
                  placeholder="e.g. Your First Jailbreak"
                  value={draft.title}
                  onChange={(e) => setField("title", e.target.value)}
                />
              </div>
              <div>
                <label className="field-label">Difficulty</label>
                <select
                  className="input"
                  value={draft.difficulty}
                  onChange={(e) => setField("difficulty", e.target.value)}
                >
                  {DIFFICULTY_OPTIONS.map((d) => (
                    <option key={d} value={d}>{formatLabel(d)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="field-label">Estimated time (minutes)</label>
                <TurnsStepper
                  value={draft.estimated_minutes}
                  onChange={(v) => setField("estimated_minutes", v)}
                  step={5}
                  min={5}
                  max={120}
                />
              </div>
            </div>
          </>
        )}

        {/* Step 2 — Learning content */}
        {step === 2 && (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Learning content</div>
              <div className="wizard-subtitle">What should students learn and observe?</div>
            </div>
            <div className="wizard-body attack-form">
              <div>
                <label className="field-label">Learning objective</label>
                <textarea
                  className="input sandbox-textarea"
                  rows={2}
                  placeholder="What the student will understand after completing this lab."
                  value={draft.learning_objective}
                  onChange={(e) => setField("learning_objective", e.target.value)}
                />
              </div>
              <div>
                <label className="field-label">
                  Description{" "}
                  <span style={{ color: "var(--text-ghost)", fontWeight: 400 }}>(optional)</span>
                </label>
                <textarea
                  className="input sandbox-textarea"
                  rows={3}
                  placeholder="Step-by-step instructions or context for the student."
                  value={draft.description}
                  onChange={(e) => setField("description", e.target.value)}
                />
              </div>
              <div>
                <label className="field-label">Success criteria</label>
                <select
                  className="input"
                  value={draft.success_criteria}
                  onChange={(e) => setField("success_criteria", e.target.value)}
                >
                  {SUCCESS_CRITERIA_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="field-label">
                  Reflection{" "}
                  <span style={{ color: "var(--text-ghost)", fontWeight: 400 }}>(optional)</span>
                </label>
                <textarea
                  className="input sandbox-textarea"
                  rows={3}
                  placeholder="Insight shown to the student after they complete the lab."
                  value={draft.reflection}
                  onChange={(e) => setField("reflection", e.target.value)}
                />
              </div>
            </div>
          </>
        )}

        {/* Step 3 — Scenario */}
        {step === 3 && (
          <>
            <div className="wizard-header">
              <div className="wizard-title">What are you testing?</div>
              <div className="wizard-subtitle">Choose a preset scenario to attack.</div>
            </div>
            <div className="wizard-body">
              <div className="scenario-grid">
                {SCENARIO_CARDS.map((card) => (
                  <button
                    key={card.name}
                    type="button"
                    className={`scenario-card${draft.pre_config.scenario === card.name ? " is-selected" : ""}`}
                    onClick={() => {
                      setConfigField("scenario", card.name);
                      setConfigField("goal", "");
                    }}
                  >
                    <div className="scenario-card-check"><Check size={12} strokeWidth={2.5} /></div>
                    <div className="scenario-card-icon"><card.Icon size={15} strokeWidth={1.5} /></div>
                    <div className="scenario-card-name">{card.name}</div>
                    <div className="scenario-card-desc">{card.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Step 4 — Objective */}
        {step === 4 && (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Select the objective</div>
              <div className="wizard-subtitle">What should the attacker try to extract?</div>
            </div>
            <div className="wizard-body">
              <div className="goal-field">
                <label className="field-label">Target objective</label>
                <select
                  className="input"
                  value={goalSelectValue}
                  onChange={(e) => {
                    const val = e.target.value;
                    setConfigField("goal", val === PRESET_PLACEHOLDER ? "" : val);
                  }}
                >
                  <option value={PRESET_PLACEHOLDER} disabled>Choose an objective</option>
                  {(SCENARIO_GOALS[draft.pre_config.scenario] || []).map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
            </div>
          </>
        )}

        {/* Step 5 — Attack params */}
        {step === 5 && (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Configure the attack</div>
              <div className="wizard-subtitle">Select your model, strategy, and run length.</div>
            </div>
            <div className="wizard-body attack-form">
              <div className="eval-grid" style={{ gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label className="field-label">Attacker model</label>
                  <select
                    className="input"
                    value={draft.pre_config.attacker_model}
                    onChange={(e) => setConfigField("attacker_model", e.target.value)}
                  >
                    {(MODEL_OPTIONS.groq || []).map((m) => (
                      <option key={m.value} value={m.value}>{m.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="field-label">Target LLM</label>
                  <select
                    className="input"
                    value={draft.pre_config.target_model}
                    onChange={(e) => setConfigField("target_model", e.target.value)}
                  >
                    {(MODEL_OPTIONS.groq || []).map((m) => (
                      <option key={m.value} value={m.value}>{m.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="field-label">Strategy</label>
                <select
                  className="input"
                  value={draft.pre_config.strategy_id}
                  onChange={(e) => setConfigField("strategy_id", e.target.value)}
                >
                  {STRATEGY_OPTIONS.map((s) => (
                    <option key={s} value={s}>{formatLabel(s)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="field-label">Max turns</label>
                <TurnsStepper
                  value={draft.pre_config.max_turns}
                  onChange={(v) => setConfigField("max_turns", v)}
                />
              </div>
              <div>
                <label className="field-label">Guardrail mode</label>
                <div className="mode-group">
                  <label className={`mode-option${draft.pre_config.dry_run ? " is-selected" : ""}`}>
                    <input
                      type="radio"
                      name="lab-mode"
                      checked={draft.pre_config.dry_run}
                      onChange={() => setConfigField("dry_run", true)}
                    />
                    <div className="mode-option-dot" />
                    <div className="mode-option-text">
                      <span className="mode-option-label">Dry run</span>
                      <span className="mode-option-desc">Flag violations without blocking</span>
                    </div>
                  </label>
                  <label className={`mode-option${!draft.pre_config.dry_run ? " is-selected" : ""}`}>
                    <input
                      type="radio"
                      name="lab-mode"
                      checked={!draft.pre_config.dry_run}
                      onChange={() => setConfigField("dry_run", false)}
                    />
                    <div className="mode-option-dot" />
                    <div className="mode-option-text">
                      <span className="mode-option-label">Enforced</span>
                      <span className="mode-option-desc">Actively block unsafe turns</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </>
        )}

        <div className="modal-actions">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => (step === 1 ? onClose() : setStep((s) => s - 1))}
          >
            <ArrowLeft size={14} /> {step === 1 ? "Cancel" : "Back"}
          </button>
          <div className="modal-actions-right">
            {step < TOTAL_STEPS ? (
              <button
                type="button"
                className="btn btn-primary"
                disabled={!canAdvance}
                onClick={() => setStep((s) => s + 1)}
              >
                Continue
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => onSave(draft)}
              >
                Save lab
              </button>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
