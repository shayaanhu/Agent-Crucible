import React from "react";
import { Crosshair, Terminal, BarChart3, GraduationCap } from "../icons";

export default function EntryView({ onSelectMode }) {
  return (
    <div className="modal-shell">
      <div className="modal-backdrop" />
      <section className="modal-card">
        <div style={{ padding: "36px 40px" }}>
          <div className="entry-header-minimal">
            <div className="entry-title-minimal">Agent Crucible</div>
            <div style={{ color: "var(--text-secondary)", fontSize: "0.9375rem" }}>
              Choose your testing environment
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              { mode: "lab",        Icon: Crosshair,      title: "Live Attack Lab",   desc: "Multi-turn red-team simulator with strategy chains and turn-by-turn visualization." },
              { mode: "sandbox",    Icon: Terminal,        title: "Attack Sandbox",    desc: "Write your own attack prompts and see the blue-team verdict in real time." },
              { mode: "labs",       Icon: GraduationCap,   title: "Lab Exercises",     desc: "Guided labs with pre-configured attacks, learning objectives, and reflection notes." },
              { mode: "evaluation", Icon: BarChart3,       title: "Testing Suite",     desc: "Automated benchmark. Run the full objective suite and view performance metrics." },
            ].map(({ mode, Icon, title, desc }) => (
              <button
                key={mode}
                type="button"
                className="entry-option"
                onClick={() => onSelectMode(mode)}
              >
                <div className="entry-option-icon">
                  <Icon size={18} strokeWidth={1.5} />
                </div>
                <div className="entry-option-body">
                  <div className="entry-option-title">{title}</div>
                  <div className="entry-option-desc">{desc}</div>
                </div>
              </button>
            ))}
          </div>

          <div style={{ textAlign: "center", marginTop: 28, opacity: 0.25, fontSize: "0.7rem", letterSpacing: "0.08em" }}>
            AGENT CRUCIBLE V1.0.0
          </div>
        </div>
      </section>
    </div>
  );
}
