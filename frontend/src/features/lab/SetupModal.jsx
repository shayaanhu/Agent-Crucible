import React from "react";
import { ArrowLeft, X, Check } from "../../icons";
import {
  SCENARIO_CARDS,
  SCENARIO_GOALS,
  PROVIDER_OPTIONS,
  MODEL_OPTIONS,
  STRATEGY_OPTIONS,
  PRESET_PLACEHOLDER,
  CUSTOM_OPTION,
} from "../../constants";
import { formatLabel, selectState } from "../../utils/format";
import TurnsStepper from "./TurnsStepper";

export default function SetupModal({
  step,
  setup,
  onField,
  onBack,
  onNext,
  onLaunch,
  onClose,
  loading,
  hasRun,
}) {
  const goalSelectValue = selectState(setup.goal, SCENARIO_GOALS[setup.scenario] || []);
  const launchReady =
    step === 1 ? Boolean(setup.scenario.trim()) :
    step === 2 ? Boolean(setup.goal.trim()) :
    step === 3 ? (Boolean(setup.attacker_model) && Boolean(setup.target_model)) :
    true;
  const validStep = step >= 1 && step <= 5;

  return (
    <div className="modal-shell">
      <div className="modal-backdrop" onClick={hasRun ? onClose : undefined} />
      <section className="modal-card">
        {hasRun ? (
          <button
            type="button"
            className="btn btn-ghost"
            style={{ position: "absolute", top: 16, right: 16, padding: "0 6px" }}
            onClick={onClose}
          >
            <X size={16} />
          </button>
        ) : null}

        <div className="step-indicator">
          <span className="step-counter">Step {step} of 5</span>
          <div className="step-dots">
            {[1, 2, 3, 4, 5].map((n) => (
              <div
                key={n}
                className={`step-dot${n < step ? " is-done" : n === step ? " is-active" : ""}`}
              />
            ))}
          </div>
        </div>

        {step === 1 ? (
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
                    className={`scenario-card${setup.scenario === card.name ? " is-selected" : ""}`}
                    onClick={() => { onField("scenario", card.name); onField("goal", ""); }}
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
        ) : null}

        {step === 2 ? (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Select your objective</div>
              <div className="wizard-subtitle">What information are you trying to extract?</div>
            </div>
            <div className="wizard-body">
              <div className="goal-field">
                <label className="field-label">Target objective</label>
                <select
                  className="input"
                  value={goalSelectValue}
                  onChange={(e) => {
                    const val = e.target.value;
                    onField("goal", val === PRESET_PLACEHOLDER ? "" : val);
                  }}
                >
                  <option value={PRESET_PLACEHOLDER} disabled>Choose your objective</option>
                  {(SCENARIO_GOALS[setup.scenario] || []).map((goal) => (
                    <option key={goal} value={goal}>{goal}</option>
                  ))}
                </select>
              </div>
            </div>
          </>
        ) : null}

        {step === 3 ? (
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
                    value={setup.attacker_model}
                    onChange={(e) => onField("attacker_model", e.target.value)}
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
                    value={setup.target_model}
                    onChange={(e) => onField("target_model", e.target.value)}
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
                  value={setup.strategyId}
                  onChange={(e) => onField("strategyId", e.target.value)}
                >
                  {/* STRATEGY_OPTIONS imported from constants in parent — passed via setup */}
                  {STRATEGY_OPTIONS.map((strategy) => (
                    <option key={strategy} value={strategy}>{formatLabel(strategy)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="field-label">Max turns</label>
                <TurnsStepper value={setup.maxTurns} onChange={(v) => onField("maxTurns", v)} />
              </div>
            </div>
          </>
        ) : null}

        {step === 4 ? (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Enforcement mode</div>
              <div className="wizard-subtitle">Choose how the guardrails should respond.</div>
            </div>
            <div className="wizard-body attack-form">
              <div>
                <label className="field-label">Guardrail behavior</label>
                <div className="mode-group">
                  <label className={`mode-option${setup.dryRun ? " is-selected" : ""}`}>
                    <input type="radio" name="mode" checked={setup.dryRun} onChange={() => onField("dryRun", true)} />
                    <div className="mode-option-dot" />
                    <div className="mode-option-text">
                      <span className="mode-option-label">Dry run</span>
                      <span className="mode-option-desc">Flag safety violations but don't block them</span>
                    </div>
                  </label>
                  <label className={`mode-option${!setup.dryRun ? " is-selected" : ""}`}>
                    <input type="radio" name="mode" checked={!setup.dryRun} onChange={() => onField("dryRun", false)} />
                    <div className="mode-option-dot" />
                    <div className="mode-option-text">
                      <span className="mode-option-label">Enforced</span>
                      <span className="mode-option-desc">Actively block unsafe turns in real time</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </>
        ) : null}

        {step === 5 ? (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Review your setup</div>
              <div className="wizard-subtitle">Confirm everything looks right, then launch.</div>
            </div>
            <div className="review-list">
              {[
                { key: "Scenario", value: setup.scenario },
                { key: "Objective", value: setup.goal },
                { key: "Attacker", value: setup.attacker_model },
                { key: "Target", value: setup.target_model },
                { key: "Strategy", value: formatLabel(setup.strategyId) },
                { key: "Turns", value: setup.maxTurns },
                { key: "Mode", value: setup.dryRun ? "Dry run" : "Enforced" },
              ].map((row) => (
                <div className="review-row" key={row.key}>
                  <span className="review-row-key">{row.key}</span>
                  <span className="review-row-value">{row.value}</span>
                </div>
              ))}
            </div>
          </>
        ) : null}

        {!validStep ? (
          <>
            <div className="wizard-header">
              <div className="wizard-title">Wizard state reset needed</div>
              <div className="wizard-subtitle">The setup step became invalid. Use Back to recover.</div>
            </div>
          </>
        ) : null}

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onBack} disabled={loading}>
            <ArrowLeft size={14} /> Back
          </button>
          <div className="modal-actions-right">
            {step < 5 ? (
              <button type="button" className="btn btn-primary" onClick={onNext} disabled={loading || !launchReady}>
                Continue
              </button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={onLaunch} disabled={loading || !launchReady}>
                {loading ? "Launching..." : "Launch run"}
              </button>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
