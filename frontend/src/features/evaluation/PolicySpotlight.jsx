import React from "react";
import { Badge } from "../../components/Badge";
import { formatLabel } from "../../utils/format";

export default function PolicySpotlight({ entries, total }) {
  return (
    <section className="eval-section">
      <div className="eval-section-title">Policy spotlight</div>
      {entries.length ? (
        <div className="policy-spotlight-list">
          {entries.map(([policyId, count], index) => {
            const pct = total ? Math.round((count / total) * 100) : 0;
            return (
              <div className="policy-spotlight-row" key={policyId}>
                <div className="policy-spotlight-rank">#{index + 1}</div>
                <div className="policy-spotlight-main">
                  <div className="policy-spotlight-name">{formatLabel(policyId)}</div>
                  <div className="policy-spotlight-meta">{count} cases</div>
                </div>
                <Badge tone="neutral">{pct}%</Badge>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="empty-copy">No policy patterns captured yet.</p>
      )}
    </section>
  );
}
