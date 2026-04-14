// Pure aggregation and analysis functions. No JSX, no React.

// ── Shared helpers ────────────────────────────────────────────────────────────

export function sortCountEntries(values) {
  return Object.entries(values || {}).sort((left, right) => {
    if (right[1] !== left[1]) return right[1] - left[1];
    return String(left[0]).localeCompare(String(right[0]));
  });
}

// ── Live run analysis ─────────────────────────────────────────────────────────

export function summarizeBlueTeam(timeline) {
  const verdicts = timeline.map((entry) => entry.verdict).filter(Boolean);
  if (!verdicts.length) {
    return { reviewed: 0, blocked: 0, highestSeverity: "n/a", dominantAction: "n/a" };
  }
  const severityRank = { low: 1, medium: 2, high: 3, critical: 4 };
  let highest = "low";
  const actions = {};
  let blocked = 0;
  verdicts.forEach((verdict) => {
    if ((severityRank[verdict.severity] || 0) > (severityRank[highest] || 0))
      highest = verdict.severity;
    actions[verdict.action] = (actions[verdict.action] || 0) + 1;
    if (verdict.action === "block" || verdict.action === "escalate") blocked += 1;
  });
  const dominantAction =
    Object.entries(actions).sort((left, right) => right[1] - left[1])[0]?.[0] || "allow";
  return { reviewed: verdicts.length, blocked, highestSeverity: highest, dominantAction };
}

export function sumBlueInterventions(summary) {
  return sortCountEntries(summary?.action_counts).reduce(
    (total, [action, count]) => total + (action === "allow" ? 0 : count),
    0
  );
}

export function summarizeBlueBenchmarkResults(results) {
  const severityRank = { low: 1, medium: 2, high: 3, critical: 4 };
  const severityCounts = {};
  let highestSeverity = "n/a";
  let totalConfidence = 0;
  let confidenceSamples = 0;
  let agreementSamples = 0;
  let multiDetectorHits = 0;
  let supportTotal = 0;

  (results || []).forEach((result) => {
    if (typeof result?.confidence === "number") {
      totalConfidence += result.confidence;
      confidenceSamples += 1;
    }
    const severity = result?.detector_results?._decision?.severity;
    if (severity) {
      severityCounts[severity] = (severityCounts[severity] || 0) + 1;
      if (
        highestSeverity === "n/a" ||
        (severityRank[severity] || 0) > (severityRank[highestSeverity] || 0)
      ) {
        highestSeverity = severity;
      }
    }
    const decision = result?.detector_results?._decision;
    const evaluations =
      result?.detector_results?._aggregation?.policy_evaluations || [];
    const selectedPolicy =
      evaluations.find(
        (item) => item.triggered && item.policy_id === decision?.selected_policy_id
      ) || evaluations.find((item) => item.triggered);
    if (selectedPolicy) {
      const supportCount =
        selectedPolicy.supporting_count ||
        selectedPolicy.supporting_detectors?.length ||
        0;
      agreementSamples += 1;
      supportTotal += supportCount;
      if (supportCount > 1) multiDetectorHits += 1;
    }
  });

  return {
    severityCounts,
    highestSeverity,
    averageConfidence: confidenceSamples ? totalConfidence / confidenceSamples : null,
    averageSupport: agreementSamples ? supportTotal / agreementSamples : null,
    multiDetectorHits,
    multiDetectorRate: agreementSamples ? multiDetectorHits / agreementSamples : null,
    agreementSamples,
  };
}

export function summarizeLiveBlueRun(timeline) {
  const severityRank = { low: 1, medium: 2, high: 3, critical: 4 };
  const actionCounts = {};
  const severityCounts = {};
  const policyCounts = {};
  const outcomeCounts = {};
  let highestSeverity = "n/a";
  let interventionCount = 0;
  let stoppedCount = 0;
  let dryRunTurns = 0;
  let totalConfidence = 0;
  let confidenceSamples = 0;
  let supportTotal = 0;
  let agreementSamples = 0;
  let multiDetectorHits = 0;

  (timeline || []).forEach((entry) => {
    const verdict = entry?.verdict || {};
    const action = verdict.action || "allow";
    const severity = verdict.severity || "low";
    const policyId = verdict.policy_id || "policy.safe.default";
    const outcome =
      entry?.event?.objective_scorer?.label ||
      entry?.event?.outcome ||
      "pending";

    actionCounts[action] = (actionCounts[action] || 0) + 1;
    severityCounts[severity] = (severityCounts[severity] || 0) + 1;
    policyCounts[policyId] = (policyCounts[policyId] || 0) + 1;
    outcomeCounts[outcome] = (outcomeCounts[outcome] || 0) + 1;

    if (action !== "allow") interventionCount += 1;
    if (action === "block" || action === "escalate") stoppedCount += 1;
    if (verdict.dry_run) dryRunTurns += 1;
    if ((severityRank[severity] || 0) > (severityRank[highestSeverity] || 0)) {
      highestSeverity = severity;
    }
    if (typeof verdict.confidence === "number") {
      totalConfidence += verdict.confidence;
      confidenceSamples += 1;
    }

    const evaluations =
      verdict?.detector_results?._aggregation?.policy_evaluations || [];
    const selectedPolicy =
      evaluations.find(
        (item) => item.triggered && item.policy_id === verdict?.policy_id
      ) || evaluations.find((item) => item.triggered);
    if (selectedPolicy) {
      const supportCount =
        selectedPolicy.supporting_count ||
        selectedPolicy.supporting_detectors?.length ||
        0;
      agreementSamples += 1;
      supportTotal += supportCount;
      if (supportCount > 1) multiDetectorHits += 1;
    }
  });

  const totalTurns = (timeline || []).length;
  const successfulTurns = outcomeCounts.success || 0;
  const defendedTurns = totalTurns - successfulTurns;

  return {
    totalTurns,
    defendedTurns,
    defendedRate: totalTurns ? defendedTurns / totalTurns : null,
    successfulTurns,
    stoppedCount,
    interventionCount,
    actionCounts,
    severityCounts,
    policyCounts,
    outcomeCounts,
    highestSeverity,
    averageConfidence: confidenceSamples ? totalConfidence / confidenceSamples : null,
    averageSupport: agreementSamples ? supportTotal / agreementSamples : null,
    multiDetectorHits,
    multiDetectorRate: agreementSamples ? multiDetectorHits / agreementSamples : null,
    dryRunTurns,
  };
}

// ── Suite / evaluation analysis ───────────────────────────────────────────────

export function computeSuiteInsights(cases) {
  if (!cases?.length) return null;

  const adversarial = cases.filter((c) => c.category !== "benign_control");
  const benign = cases.filter((c) => c.category === "benign_control");

  const byCategory = {};
  const byDifficulty = {};
  const byStrategy = {};

  adversarial.forEach((c) => {
    const cat = c.category || "uncategorized";
    const diff = c.difficulty || "unspecified";
    const strat = c.strategy_id || c.turns?.[0]?.strategy_id || "unknown";
    const breached = c.final_outcome === "success";

    if (!byCategory[cat]) byCategory[cat] = { total: 0, succeeded: 0 };
    byCategory[cat].total++;
    if (breached) byCategory[cat].succeeded++;

    if (!byDifficulty[diff]) byDifficulty[diff] = { total: 0, succeeded: 0 };
    byDifficulty[diff].total++;
    if (breached) byDifficulty[diff].succeeded++;

    if (!byStrategy[strat]) byStrategy[strat] = { total: 0, succeeded: 0 };
    byStrategy[strat].total++;
    if (breached) byStrategy[strat].succeeded++;
  });

  const succeeded = adversarial.filter((c) => c.final_outcome === "success");
  const blueMissed = succeeded.filter((c) => !c.blue_team_any_blocked).length;
  const overRefusals = benign.filter((c) => c.blue_team_any_blocked).length;

  const weakestCategory =
    Object.entries(byCategory)
      .map(([cat, d]) => ({ cat, rate: d.total ? d.succeeded / d.total : 0 }))
      .sort((a, b) => b.rate - a.rate)[0] || null;

  return {
    adversarialTotal: adversarial.length,
    adversarialSucceeded: succeeded.length,
    benignTotal: benign.length,
    blueMissed,
    blueMissRate: succeeded.length ? blueMissed / succeeded.length : null,
    overRefusals,
    overRefusalRate: benign.length ? overRefusals / benign.length : null,
    byCategory,
    byDifficulty,
    byStrategy,
    weakestCategory,
  };
}

export function computeSuiteSummary(cases) {
  if (!cases?.length) return null;
  const total = cases.length;
  const succeeded = cases.filter((c) => c.final_outcome === "success").length;
  const defended = cases.filter((c) => c.final_outcome === "blocked").length;
  const guardrailFired = cases.filter((c) => c.blue_team_any_blocked).length;
  const totalTurns = cases.reduce((s, c) => s + (c.turns?.length || 0), 0);
  return {
    total,
    succeeded,
    defended,
    guardrailFired,
    attackRate: total ? succeeded / total : 0,
    avgTurns: total ? Math.round((totalTurns / total) * 10) / 10 : 0,
  };
}

export function summarizeSuiteBlueTeam(cases) {
  const severityRank = { low: 1, medium: 2, high: 3, critical: 4 };
  const actionCounts = {};
  const severityCounts = {};
  let interventionCount = 0;
  let stoppedCount = 0;
  let highestSeverity = "n/a";
  let totalVerdicts = 0;

  (cases || []).forEach((c) => {
    (c.blue_team_verdicts || []).forEach((v) => {
      const action = v.action || "allow";
      const severity = v.severity || "low";
      actionCounts[action] = (actionCounts[action] || 0) + 1;
      severityCounts[severity] = (severityCounts[severity] || 0) + 1;
      if (action !== "allow") interventionCount += 1;
      if (action === "block" || action === "escalate") stoppedCount += 1;
      if (
        highestSeverity === "n/a" ||
        (severityRank[severity] || 0) > (severityRank[highestSeverity] || 0)
      ) {
        highestSeverity = severity;
      }
      totalVerdicts += 1;
    });
  });

  return {
    totalVerdicts,
    actionCounts,
    severityCounts,
    interventionCount,
    stoppedCount,
    highestSeverity,
  };
}
