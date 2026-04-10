import React from "react";
export function Badge({ tone = "neutral", children }) {
  const cls =
    tone === "safe"
      ? "success"
      : tone === "info"
      ? "info"
      : tone === "warning"
      ? "warning"
      : tone === "danger"
      ? "danger"
      : "neutral";
  return <span className={`badge badge-${cls}`}>{children}</span>;
}

// Legacy alias kept for drawer components.
export function Pill({ tone = "neutral", children }) {
  return <Badge tone={tone}>{children}</Badge>;
}

export default Badge;
