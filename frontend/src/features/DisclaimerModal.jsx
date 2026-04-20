import React from "react";
import { ShieldIcon, Check } from "../icons";

const ITEMS = [
  "This tool generates adversarial prompts against language models. I will only use it for authorized security research, classroom exercises, or personal learning.",
  "I will not use Agent Crucible to attack production systems, third-party APIs, or any model I do not have explicit permission to test.",
  "I understand that attack strategies demonstrated here reflect real-world techniques. I accept responsibility for how I apply this knowledge.",
  "I acknowledge that the goal of this platform is to teach defense — understanding how attacks work so they can be prevented.",
];

export default function DisclaimerModal({ onAccept }) {
  return (
    <div className="modal-shell disclaimer-shell">
      <div className="modal-backdrop" />
      <section className="modal-card disclaimer-card">

        <div className="disclaimer-icon-row">
          <div className="disclaimer-icon-wrap">
            <ShieldIcon size={22} strokeWidth={1.5} />
          </div>
        </div>

        <div className="disclaimer-header">
          <div className="disclaimer-title">Dual-Use Research Tool</div>
          <div className="disclaimer-subtitle">
            Agent Crucible is built for education and security research. Before you continue,
            please read and acknowledge the following.
          </div>
        </div>

        <div className="disclaimer-items">
          {ITEMS.map((text, i) => (
            <div key={i} className="disclaimer-item">
              <div className="disclaimer-check">
                <Check size={11} strokeWidth={2.5} />
              </div>
              <span>{text}</span>
            </div>
          ))}
        </div>

        <div className="disclaimer-footer">
          <button
            type="button"
            className="disclaimer-btn"
            onClick={onAccept}
          >
            I understand — continue
          </button>
          <div className="disclaimer-note">
            This acknowledgement is stored locally and won't appear again.
          </div>
        </div>

      </section>
    </div>
  );
}
