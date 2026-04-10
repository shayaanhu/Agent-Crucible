import React from "react";
import { isEmpty } from "../utils/format";

export default function KeyGrid({ items }) {
  return (
    <div className="key-grid">
      {items.filter((item) => !isEmpty(item.value)).map((item) => (
        <div className="key-cell" key={item.label}>
          <div className="key-label">{item.label}</div>
          <div className="key-value">{item.value}</div>
        </div>
      ))}
    </div>
  );
}
