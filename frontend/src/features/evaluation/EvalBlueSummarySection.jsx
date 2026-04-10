import React, { useMemo } from "react";
import { Badge } from "../../components/Badge";
import SectionHeader from "../../components/SectionHeader";
import StatCard from "../../components/StatCard";
import DistributionTable from "../../components/DistributionTable";
import { summarizeSuiteBlueTeam, sortCountEntries } from "../../utils/analysis";
import { formatLabel, toneForAction, toneForSeverity } from "../../utils/format";

export default function EvalBlueSummarySection({ cases }) {
  const insights = useMemo(() => summarizeSuiteBlueTeam(cases), [cases]);
  const actionEntries = useMemo(() => sortCountEntries(insights.actionCounts), [insights]);
  const severityEntries = useMemo(() => sortCountEntries(insights.severityCounts), [insights]);

  if (!insights.totalVerdicts) return null;

  return (
    <section className="live-blue-team-section">
      <SectionHeader
        title="Blue-team overview"
        note="Aggregated guardrail activity across all suite cases."
        actions={<Badge tone="neutral">{insights.totalVerdicts} verdicts</Badge>}
      />
      <div className="stat-bar">
        <StatCard label="Unsafe stopped" value={insights.stoppedCount} />
        <StatCard label="Actioned responses" value={insights.interventionCount} />
        <StatCard label="Highest severity" value={formatLabel(insights.highestSeverity)} />
      </div>
      <div className="eval-grid">
        <DistributionTable
          title="Action mix"
          entries={actionEntries}
          total={insights.totalVerdicts}
          toneForKey={toneForAction}
          emptyLabel="No blue-team action data."
        />
        <DistributionTable
          title="Severity mix"
          entries={severityEntries}
          total={insights.totalVerdicts}
          toneForKey={toneForSeverity}
          emptyLabel="No severity data."
        />
      </div>
    </section>
  );
}
