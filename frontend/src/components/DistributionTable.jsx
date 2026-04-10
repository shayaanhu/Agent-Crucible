import React from "react";
import { Badge } from "./Badge";
import { formatLabel, formatNumber } from "../utils/format";

// Shared between the Live Attack Lab's benchmark section and the Evaluation view.
export default function DistributionTable({
  title,
  entries,
  total,
  toneForKey = () => "neutral",
  emptyLabel = "No data available yet.",
}) {
  return (
    <section className="eval-section">
      <div className="eval-section-title">{title}</div>
      {entries.length ? (
        <div className="distribution-list">
          {entries.map(([key, value]) => {
            const pct = total
              ? Math.max(0, Math.min(100, Math.round((value / total) * 100)))
              : 0;
            return (
              <div className="distribution-row" key={key}>
                <div className="distribution-row-top">
                  <div className="distribution-row-label">{formatLabel(key)}</div>
                  <div className="distribution-row-value">
                    <span>{typeof value === "number" ? formatNumber(value) : value}</span>
                    <Badge tone={toneForKey(key)}>{pct}%</Badge>
                  </div>
                </div>
                <div className="distribution-meter">
                  <div
                    className={`distribution-meter-fill tone-${toneForKey(key)}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="empty-copy">{emptyLabel}</p>
      )}
    </section>
  );
}
