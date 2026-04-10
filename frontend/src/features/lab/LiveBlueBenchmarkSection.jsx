import React, { useMemo } from "react";
import { Badge } from "../../components/Badge";
import SectionHeader from "../../components/SectionHeader";
import StatCard from "../../components/StatCard";
import KeyGrid from "../../components/KeyGrid";
import Fold from "../../components/Fold";
import DetailPre from "../../components/DetailPre";
import DistributionTable from "../../components/DistributionTable";
import LiveBlueTurnTraceList from "./LiveBlueTurnTraceList";
import { summarizeLiveBlueRun, sortCountEntries } from "../../utils/analysis";
import {
  formatNumber,
  formatSignedCount,
  toneForAction,
  toneForSeverity,
  toneForOutcome,
  formatLabel,
} from "../../utils/format";

export default function LiveBlueBenchmarkSection({ timeline }) {
  const liveInsights = useMemo(() => summarizeLiveBlueRun(timeline), [timeline]);
  const successRate = liveInsights.totalTurns
    ? liveInsights.successfulTurns / liveInsights.totalTurns
    : null;
  const turnDelta =
    typeof liveInsights.defendedTurns === "number" &&
    typeof liveInsights.successfulTurns === "number"
      ? liveInsights.defendedTurns - liveInsights.successfulTurns
      : null;

  const actionEntries = useMemo(
    () => sortCountEntries(liveInsights.actionCounts),
    [liveInsights]
  );
  const severityEntries = useMemo(
    () => sortCountEntries(liveInsights.severityCounts),
    [liveInsights]
  );
  const policyEntries = useMemo(
    () => sortCountEntries(liveInsights.policyCounts).slice(0, 4),
    [liveInsights]
  );
  const outcomeEntries = useMemo(
    () => sortCountEntries(liveInsights.outcomeCounts),
    [liveInsights]
  );
  const importantTurnTraces = useMemo(() => {
    const severityRank = { low: 1, medium: 2, high: 3, critical: 4 };
    const sorted = [...(timeline || [])].sort((left, right) => {
      const leftOutcome =
        left?.event?.objective_scorer?.label || left?.event?.outcome || "pending";
      const rightOutcome =
        right?.event?.objective_scorer?.label || right?.event?.outcome || "pending";
      if (leftOutcome !== rightOutcome) {
        if (leftOutcome === "success") return -1;
        if (rightOutcome === "success") return 1;
      }
      return (
        (severityRank[right?.verdict?.severity] || 0) -
        (severityRank[left?.verdict?.severity] || 0)
      );
    });
    return sorted.slice(0, 6);
  }, [timeline]);

  return (
    <section className="live-blue-team-section">
      <SectionHeader
        title="Blue-team overview"
        note="Keep defense outcome, policy patterns, and turn movement next to the live run."
        actions={<Badge tone="neutral">{liveInsights.totalTurns} turns</Badge>}
      />

      {!!liveInsights.totalTurns && (
        <>
          <div className="stat-bar">
            <StatCard
              label="Defense outcome"
              value={liveInsights.defendedRate === null ? "n/a" : formatNumber(liveInsights.defendedRate)}
            />
            <StatCard label="Unsafe stopped" value={liveInsights.stoppedCount} />
            <StatCard label="Actioned responses" value={liveInsights.interventionCount} />
          </div>

          <div className="eval-grid">
            <DistributionTable
              title="Action mix"
              entries={actionEntries}
              total={liveInsights.totalTurns}
              toneForKey={toneForAction}
              emptyLabel="No blue-team action data yet."
            />
            <DistributionTable
              title="Severity mix"
              entries={severityEntries}
              total={liveInsights.totalTurns}
              toneForKey={toneForSeverity}
              emptyLabel="No severity signal captured yet."
            />
          </div>

          <Fold title="More blue-team details">
            <div className="eval-grid">
              <section className="eval-section">
                <div className="eval-section-title">Confidence and detector agreement</div>
                <KeyGrid
                  items={[
                    { label: "Average confidence", value: formatNumber(liveInsights.averageConfidence) },
                    { label: "Average detector support", value: formatNumber(liveInsights.averageSupport) },
                    {
                      label: "Multi-detector hits",
                      value:
                        liveInsights.multiDetectorRate === null
                          ? "n/a"
                          : `${liveInsights.multiDetectorHits} (${formatNumber(liveInsights.multiDetectorRate)})`,
                    },
                    { label: "Highest severity", value: formatLabel(liveInsights.highestSeverity) },
                    { label: "Dry-run turns", value: liveInsights.dryRunTurns },
                    { label: "Defended turns", value: liveInsights.defendedTurns },
                  ]}
                />
              </section>

              <section className="eval-section">
                <div className="eval-section-title">Run comparison</div>
                <KeyGrid
                  items={[
                    { label: "Defense outcome", value: formatNumber(liveInsights.defendedRate) },
                    { label: "Attack success rate", value: formatNumber(successRate) },
                    { label: "Turn delta", value: formatSignedCount(turnDelta) },
                    { label: "Allowed turns", value: liveInsights.actionCounts.allow || 0 },
                    { label: "Stopped turns", value: liveInsights.stoppedCount },
                    {
                      label: "Dominant policy",
                      value: policyEntries[0] ? formatLabel(policyEntries[0][0]) : "n/a",
                    },
                  ]}
                />
              </section>
            </div>

            <div className="eval-grid">
              <DistributionTable
                title="Policy counts"
                entries={sortCountEntries(liveInsights.policyCounts)}
                total={liveInsights.totalTurns}
                emptyLabel="No policy distribution available yet."
              />
              <DistributionTable
                title="Outcome mix"
                entries={outcomeEntries}
                total={liveInsights.totalTurns}
                toneForKey={toneForOutcome}
                emptyLabel="No outcome distribution available yet."
              />
            </div>

            <section className="eval-section">
              <div className="eval-section-title">Turn defense traces</div>
              <LiveBlueTurnTraceList entries={importantTurnTraces} />
            </section>

            <Fold title="Raw live run timeline">
              <DetailPre text={JSON.stringify(timeline || [], null, 2)} />
            </Fold>
          </Fold>
        </>
      )}
    </section>
  );
}
