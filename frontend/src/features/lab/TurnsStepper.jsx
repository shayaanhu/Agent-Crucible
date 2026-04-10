import React, { useState, useEffect } from "react";
import { ChevronDown, ChevronUp } from "../../icons";

export default function TurnsStepper({ value, onChange }) {
  const [raw, setRaw] = useState(String(value));
  useEffect(() => { setRaw(String(value)); }, [value]);

  function commit(str) {
    const n = parseInt(str, 10);
    onChange(isNaN(n) || n < 1 ? 1 : Math.min(n, 10));
  }

  return (
    <div className="stepper-v">
      <button
        type="button"
        className="stepper-v-btn"
        onClick={() => onChange(Math.max(1, value - 1))}
        disabled={value <= 1}
      >
        <ChevronDown size={14} strokeWidth={2} />
      </button>
      <input
        className="stepper-v-display"
        type="text"
        inputMode="numeric"
        value={raw}
        onChange={(e) => setRaw(e.target.value.replace(/[^0-9]/g, ""))}
        onBlur={(e) => { commit(e.target.value); }}
        onKeyDown={(e) => { if (e.key === "Enter") { commit(raw); e.target.blur(); } }}
      />
      <button
        type="button"
        className="stepper-v-btn"
        onClick={() => onChange(Math.min(10, value + 1))}
        disabled={value >= 10}
      >
        <ChevronUp size={14} strokeWidth={2} />
      </button>
    </div>
  );
}
