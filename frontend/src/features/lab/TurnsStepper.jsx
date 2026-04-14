import React, { useState, useEffect } from "react";
import { ChevronDown, ChevronUp } from "../../icons";

export default function TurnsStepper({ value, onChange, step = 1, min = 1, max = 10 }) {
  const [raw, setRaw] = useState(String(value));
  useEffect(() => { setRaw(String(value)); }, [value]);

  function commit(str) {
    const n = parseInt(str, 10);
    if (isNaN(n)) { setRaw(String(value)); return; }
    const clamped = Math.max(min, Math.min(max, Math.round(n / step) * step));
    setRaw(String(clamped));
    onChange(clamped);
  }

  return (
    <div className="stepper-v">
      <button
        type="button"
        className="stepper-v-btn"
        onClick={() => onChange(Math.max(min, value - step))}
        disabled={value <= min}
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
        onClick={() => onChange(Math.min(max, value + step))}
        disabled={value >= max}
      >
        <ChevronUp size={14} strokeWidth={2} />
      </button>
    </div>
  );
}
