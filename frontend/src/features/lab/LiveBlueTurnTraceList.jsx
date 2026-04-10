import React from "react";
import { Badge } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import {
  toneForOutcome,
  toneForAction,
  formatLabel,
  formatNumber,
  truncateMiddle,
} from "../../utils/format";

export default function LiveBlueTurnTraceList({ entries }) {
  if (!entries?.length) {
    return <p className="empty-copy">No live turn traces available yet.</p>;
  }

  return (
    <div className="blue-trace-list">
      {entries.map((entry) => {
        const verdict = entry?.verdict || {};
        const outcome =
          entry?.event?.objective_scorer?.label ||
          entry?.event?.outcome ||
          "pending";
        return (
          <div
            className="blue-trace-card"
            key={`${entry.event?.turn_index}-${entry.event?.timestamp}`}
          >
            <div className="blue-trace-top">
              <div>
                <div className="blue-trace-title">Turn {entry.event?.turn_index}</div>
                <div className="blue-trace-meta">
                  {truncateMiddle(verdict.policy_id || "policy.safe.default", 18, 16)}
                </div>
              </div>
              <div className="chip-row">
                <Badge tone={toneForOutcome(outcome)}>{formatLabel(outcome)}</Badge>
                <Badge tone={toneForAction(verdict.action)}>{formatLabel(verdict.action || "allow")}</Badge>
              </div>
            </div>
            <KeyGrid
              items={[
                { label: "Severity", value: formatLabel(verdict.severity || "low") },
                { label: "Confidence", value: formatNumber(verdict.confidence) },
                { label: "Dry run", value: verdict.dry_run ? "Yes" : "No" },
                { label: "Objective", value: formatLabel(outcome) },
              ]}
            />
            <Fold title="Detector trace">
              <DetailPre text={JSON.stringify(verdict.detector_results || {}, null, 2)} />
            </Fold>
          </div>
        );
      })}
    </div>
  );
}
