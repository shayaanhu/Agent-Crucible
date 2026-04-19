import React from "react";
import { Badge } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import { formatLabel, formatNumber } from "../../utils/format";

const ADAPTER_META = {
  llamaguard_detector: {
    label: "LlamaGuard",
    maker: "Meta",
    weight: 0.9,
    what: "A safety classifier model (Llama-Guard-3-8B) that reads each output and returns SAFE or UNSAFE with a category. Unlike regex rules, it understands context and semantics — catching disguised or paraphrased violations that literal patterns miss.",
    how: "Attempts to run as a local HuggingFace pipeline via transformers. If the model isn't downloaded or the library fails, it automatically falls back to Groq API for the same SAFE/UNSAFE classification. The result label and category are mapped to a policy ID before entering aggregation.",
    why: "Adds a model-backed second opinion on top of the rule detector, substantially reducing false negatives on novel phrasing. Weighted at 0.9 in aggregation.",
    result: "Flagged → classifier returned UNSAFE and matched a harm category (jailbreak, toxic, unsafe instruction, sensitive data, medical, prompt injection) — fed into aggregation at weight 0.9. Clean → returned SAFE, non-blocking signal sent. Error → classification failed, safe fallback used — does not influence the verdict.",
  },
  nemo_guardrails_detector: {
    label: "NeMo Guardrails",
    maker: "NVIDIA",
    weight: 0.9,
    what: "A declarative rail system that wraps an LLM with configurable guardrail rules written in Colang. It intercepts content at the conversation level and can enforce topic bans, jailbreak rails, and custom policies defined outside the code.",
    how: "Attempts to initialise NeMo rails from the Colang config directory. If the library is incompatible with the current Python version (e.g. Python 3.14), it automatically falls back to Groq API with the same SAFE/UNSAFE prompt. The result enters aggregation identically to the native rails path.",
    why: "Provides a policy-as-config layer that teams can tune without code changes — ideal for iterating on safety rules in production. Weighted at 0.9 alongside LlamaGuard.",
    result: "Flagged → rails or Groq fallback classified the output as UNSAFE — category mapped to a policy ID and weighted at 0.9 in aggregation. Clean → output classified as SAFE, non-blocking. Error → both rails and fallback failed — safe signal used, verdict unaffected.",
  },
};

export default function SandboxBlueTeamEvidence({ verdict }) {
  if (!verdict) return null;
  const dr = verdict.detector_results || {};
  const decision = dr._decision || {};
  const aggregation = dr._aggregation || {};
  const detectorEntries = Object.entries(dr).filter(([k]) => !k.startsWith("_"));
  const policyEvals = aggregation.policy_evaluations || [];
  const activeDetectors = aggregation.active_detectors || [];

  const adapters = Object.entries(ADAPTER_META).map(([id, meta]) => {
    const active = activeDetectors.includes(id);
    const result = dr[id];
    const signals = result?.signals || [];
    const flagged = active && signals.some((s) => s.flagged);
    // Read actual backend status from signal metadata
    const sigStatus = signals[0]?.metadata?.status || (active ? "active" : "off");
    const working = active && sigStatus === "active";
    const degraded = active && ["error", "unavailable", "unconfigured"].includes(sigStatus);
    const degradedReason = signals[0]?.metadata?.reason || sigStatus;
    return { id, ...meta, active, flagged, working, degraded, degradedReason, sigStatus };
  });

  return (
    <div style={{ display: "grid", gap: 14 }}>
      {/* Adapter status strip */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <span className="micro-copy" style={{ opacity: 0.6 }}>Adapters</span>
        {adapters.map(({ id, label, active, flagged, working, degraded, degradedReason }) => {
          const bg = !active
            ? "var(--surface-2, #2a2a2a)"
            : degraded
            ? "color-mix(in srgb, #faad1433 100%, transparent)"
            : flagged
            ? "color-mix(in srgb, var(--badge-danger-bg, #ff4d4f33) 100%, transparent)"
            : "color-mix(in srgb, var(--badge-safe-bg, #52c41a33) 100%, transparent)";
          const color = !active
            ? "var(--text-secondary, #666)"
            : degraded
            ? "#ffc53d"
            : flagged
            ? "var(--badge-danger-text, #ff7875)"
            : "var(--badge-safe-text, #95de64)";
          const borderColor = !active
            ? "var(--border, #333)"
            : degraded
            ? "#d48806"
            : flagged
            ? "var(--badge-danger-text, #ff4d4f)"
            : "var(--badge-safe-text, #52c41a)";
          const titleText = !active
            ? `${label}: not loaded`
            : degraded
            ? `${label}: ${degradedReason}`
            : flagged
            ? `${label}: flagged`
            : `${label}: active – clean`;
          return (
            <span key={id} title={titleText} style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              padding: "2px 9px", borderRadius: 20, fontSize: 11,
              fontWeight: 600, letterSpacing: "0.02em",
              background: bg, color, border: "1px solid", borderColor,
            }}>
              <span style={{ fontSize: 9 }}>{active ? "⬤" : "○"}</span>
              {label}
              {degraded && <span style={{ opacity: 0.75 }}>· error</span>}
              {working && flagged && <span style={{ opacity: 0.65 }}>· flagged</span>}
              {working && !flagged && <span style={{ opacity: 0.65 }}>· clean</span>}
              {!active && <span style={{ opacity: 0.45 }}>· off</span>}
            </span>
          );
        })}
      </div>

      {/* Adapter explainer */}
      <Fold title="About these adapters">
        <div style={{ display: "grid", gap: 12 }}>
          {adapters.map(({ id, label, active, flagged, degraded, degradedReason }) => {
            const meta = ADAPTER_META[id];
            return (
              <div
                key={id}
                style={{
                  padding: "10px 12px",
                  borderRadius: 6,
                  background: "var(--surface-2, #1e1e1e)",
                  border: "1px solid var(--border, #2e2e2e)",
                  display: "grid",
                  gap: 6,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: 13 }}>{label}</span>
                  <span className="micro-copy" style={{ opacity: 0.5 }}>by {meta.maker}</span>
                  <span className="micro-copy" style={{ opacity: 0.5, marginLeft: "auto" }}>
                    weight {meta.weight} ·{" "}
                    <span style={{ color: !active ? "var(--text-secondary,#666)" : degraded ? "#ffc53d" : flagged ? "var(--badge-danger-text,#ff7875)" : "var(--badge-safe-text,#95de64)" }}>
                      {!active ? "off" : degraded ? `error: ${degradedReason}` : flagged ? "flagged" : "active"}
                    </span>
                  </span>
                </div>
                <p className="micro-copy" style={{ opacity: 0.85, lineHeight: 1.6, margin: 0 }}>
                  <strong>What: </strong>{meta.what}
                </p>
                <p className="micro-copy" style={{ opacity: 0.85, lineHeight: 1.6, margin: 0 }}>
                  <strong>How: </strong>{meta.how}
                </p>
                <p className="micro-copy" style={{ opacity: 0.85, lineHeight: 1.6, margin: 0 }}>
                  <strong>Why it matters: </strong>{meta.why}
                </p>
                <p className="micro-copy" style={{ lineHeight: 1.6, margin: 0, opacity: 0.7,
                  borderTop: "1px solid var(--border, #2e2e2e)", paddingTop: 6, marginTop: 2 }}>
                  <strong style={{ color: !active ? "var(--text-secondary,#666)" : degraded ? "#ffc53d" : flagged ? "var(--badge-danger-text,#ff7875)" : "var(--badge-safe-text,#95de64)" }}>
                    {!active ? "Off" : degraded ? "Error" : flagged ? "Flagged" : "Clean"} →{" "}
                  </strong>
                  {meta.result}
                </p>
              </div>
            );
          })}
          <p className="micro-copy" style={{ opacity: 0.5, margin: 0, lineHeight: 1.6 }}>
            Both adapters run alongside the <strong>Rule Detector</strong> (regex/pattern matching, weight 1.0).
            All three signals feed the aggregation engine — if any detector reaches its policy threshold,
            the verdict is unsafe. If a dependency is missing or unconfigured, that adapter degrades
            gracefully to a non-blocking safe signal and the rule detector remains the sole enforcer.
          </p>
        </div>
      </Fold>

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
