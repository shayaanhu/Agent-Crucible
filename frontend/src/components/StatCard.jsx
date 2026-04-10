import React from "react";
export function StatCard({ label, value }) {
  return (
    <div className="stat-cell">
      <div className="stat-cell-label">{label}</div>
      <div className="stat-cell-value">{value}</div>
    </div>
  );
}

export function MiniMetric({ label, value }) {
  return (
    <div className="key-cell">
      <div className="key-label">{label}</div>
      <div style={{ marginTop: 2, fontSize: "0.8125rem", fontWeight: 600, color: "var(--text-primary)" }}>
        {value}
      </div>
    </div>
  );
}

export default StatCard;
