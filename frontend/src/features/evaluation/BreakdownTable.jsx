import React from "react";
import { formatLabel } from "../../utils/format";

export default function BreakdownTable({ title, rows }) {
  return (
    <section className="eval-section">
      <div className="eval-section-title">{title}</div>
      {rows.length ? (
        <div className="breakdown-list">
          {rows.map((row) => {
            const pct = Math.max(0, Math.min(100, Math.round((row.success_rate || 0) * 100)));
            return (
              <div className="breakdown-item" key={row.key}>
                <div className="breakdown-item-top">
                  <div>
                    <div className="breakdown-item-name">{formatLabel(row.key)}</div>
                    <div className="breakdown-item-sub">{row.cases} cases · {row.successes} success</div>
                  </div>
                  <span className="breakdown-item-pct">{pct}%</span>
                </div>
                <div className="meter-shell">
                  <div className="meter-fill" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="empty-copy">No data available yet.</p>
      )}
    </section>
  );
}
