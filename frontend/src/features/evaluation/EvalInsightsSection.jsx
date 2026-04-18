import React, { useMemo } from "react";
import { Badge } from "../../components/Badge";
import { computeSuiteInsights } from "../../utils/analysis";
import { formatLabel } from "../../utils/format";

function toneForRate(rate) {
  if (rate === 0) return "safe";
  if (rate < 0.5) return "warning";
  return "danger";
}

function pct(rate) {
  return `${Math.round(rate * 100)}%`;
}

function RateRow({ label, succeeded, total }) {
  const breachRate = total ? succeeded / total : 0;
  const defenseRate = 1 - breachRate;
  const defended = total - succeeded;
  const tone = toneForRate(breachRate);
  return (
    <div className="insights-rate-row">
      <div className="insights-rate-top">
        <span className="insights-rate-label">{formatLabel(label)}</span>
        <span className={`insights-rate-value tone-${tone}`}>
          {defended}/{total}
        </span>
      </div>
      <div className="insights-rate-bar">
        <div
          className={`insights-rate-fill tone-${tone}`}
          style={{ width: defenseRate === 0 ? "2px" : pct(defenseRate) }}
        />
      </div>
    </div>
  );
}

function BreakdownSection({ title, entries }) {
  if (!entries.length) return null;
  return (
    <section className="eval-section">
      <div className="eval-section-title">{title}</div>
      <div className="insights-rate-list">
        {entries.map(([key, data]) => (
          <RateRow key={key} label={key} succeeded={data.succeeded} total={data.total} />
        ))}
      </div>
    </section>
  );
}

export default function EvalInsightsSection({ cases }) {
  const insights = useMemo(() => computeSuiteInsights(cases), [cases]);
  if (!insights || insights.adversarialTotal === 0) return null;

  const { adversarialTotal, adversarialSucceeded, blueMissed, overRefusals, benignTotal, weakestCategory } = insights;

  let verdict;
  if (adversarialSucceeded === 0) {
    verdict = `All ${adversarialTotal} adversarial cases were defended.`;
  } else {
    const weakLabel = weakestCategory?.rate > 0 ? formatLabel(weakestCategory.cat) : null;
    const weakPart = weakLabel ? ` Weakest category: ${weakLabel} (${pct(weakestCategory.rate)} breach rate).` : "";
    const missPart =
      adversarialSucceeded > 0
        ? ` Blue team missed ${blueMissed} of ${adversarialSucceeded} breach${adversarialSucceeded !== 1 ? "es" : ""}.`
        : "";
    verdict = `${adversarialSucceeded} of ${adversarialTotal} adversarial cases breached the defense.${weakPart}${missPart}`;
  }

  const difficultyOrder = { easy: 0, medium: 1, hard: 2 };
  const categoryEntries = Object.entries(insights.byCategory).sort(
    (a, b) => b[1].succeeded / (b[1].total || 1) - a[1].succeeded / (a[1].total || 1)
  );
  const difficultyEntries = Object.entries(insights.byDifficulty).sort(
    (a, b) => (difficultyOrder[a[0]] ?? 9) - (difficultyOrder[b[0]] ?? 9)
  );
  const strategyEntries = Object.entries(insights.byStrategy).sort(
    (a, b) => b[1].succeeded / (b[1].total || 1) - a[1].succeeded / (a[1].total || 1)
  );

  return (
    <section className="eval-insights">
      <div className="eval-insights-verdict">
        <span className="eval-insights-verdict-text">{verdict}</span>
        {benignTotal > 0 && (
          <Badge tone={overRefusals > 0 ? "warning" : "safe"}>
            {overRefusals > 0
              ? `${overRefusals} over-refusal${overRefusals !== 1 ? "s" : ""}`
              : "No over-refusals"}
          </Badge>
        )}
      </div>

      <div className="eval-grid">
        <BreakdownSection title="By attack category" entries={categoryEntries} />
        <BreakdownSection title="By difficulty" entries={difficultyEntries} />
        {strategyEntries.length > 1 && (
          <BreakdownSection title="By strategy" entries={strategyEntries} />
        )}
        {benignTotal > 0 && (
          <section className="eval-section">
            <div className="eval-section-title">Blue-team coverage</div>
            <div className="insights-coverage-list">
              <div className="insights-coverage-row">
                <span className="insights-coverage-label">Breaches flagged by guardrail</span>
                <Badge tone={blueMissed === 0 ? "safe" : "warning"}>
                  {adversarialSucceeded - blueMissed} / {adversarialSucceeded}
                </Badge>
              </div>
              <div className="insights-coverage-row">
                <span className="insights-coverage-label">Benign cases over-refused</span>
                <Badge tone={overRefusals === 0 ? "safe" : "warning"}>
                  {overRefusals} / {benignTotal}
                </Badge>
              </div>
            </div>
          </section>
        )}
      </div>
    </section>
  );
}
