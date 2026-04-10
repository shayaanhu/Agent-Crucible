import React from "react";
export default function SectionHeader({ title, note, actions }) {
  return (
    <div className="section-header">
      <div>
        <div className="section-title">{title}</div>
        {note ? <div className="section-note">{note}</div> : null}
      </div>
      {actions ? <div className="header-actions">{actions}</div> : null}
    </div>
  );
}
