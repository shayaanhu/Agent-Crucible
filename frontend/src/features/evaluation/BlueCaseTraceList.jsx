import React from "react";
import { Badge } from "../../components/Badge";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import {
  toneForAction,
  formatLabel,
  formatNumber,
  truncateMiddle,
} from "../../utils/format";

export default function BlueCaseTraceList({ results }) {
  if (!results?.length) {
    return <p className="empty-copy">No case traces available yet.</p>;
  }

  return (
    <div className="blue-trace-list">
      {results.map((result) => (
        <div className="blue-trace-card" key={result.id}>
          <div className="blue-trace-top">
            <div>
              <div className="blue-trace-title">{formatLabel(result.id)}</div>
              <div className="blue-trace-meta">{truncateMiddle(result.actual_policy_id, 18, 16)}</div>
            </div>
            <div className="chip-row">
              <Badge tone={result.passed ? "safe" : "danger"}>
                {result.passed ? "Pass" : "Fail"}
              </Badge>
              <Badge tone={toneForAction(result.actual_action)}>
                {formatLabel(result.actual_action)}
              </Badge>
            </div>
          </div>
          <KeyGrid
            items={[
              { label: "Expected policy", value: truncateMiddle(result.expected_policy_id, 18, 16) },
              { label: "Allowed", value: result.actual_effective_allowed ? "Yes" : "No" },
              { label: "Confidence", value: formatNumber(result.confidence) },
              {
                label: "Severity",
                value: formatLabel(result.detector_results?._decision?.severity || "n/a"),
              },
            ]}
          />
          <Fold title="Detector trace">
            <DetailPre text={JSON.stringify(result.detector_results || {}, null, 2)} />
          </Fold>
        </div>
      ))}
    </div>
  );
}
