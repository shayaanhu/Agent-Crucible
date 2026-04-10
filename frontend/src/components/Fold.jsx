import React from "react";
export default function Fold({ title, children, defaultOpen = false }) {
  return (
    <details className="fold" open={defaultOpen}>
      <summary>{title}</summary>
      <div className="fold-body">{children}</div>
    </details>
  );
}
