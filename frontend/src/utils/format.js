// Pure formatting and data-shaping utilities. No JSX, no React.
import { PRESET_PLACEHOLDER, CUSTOM_OPTION } from "../constants";

export function isEmpty(value) {
  return value === null || value === undefined || value === "";
}

export function formatLabel(value) {
  if (isEmpty(value)) return "n/a";
  return String(value)
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/[._-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

export function formatTimestamp(value) {
  if (isEmpty(value)) return "No timestamp";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

export function formatNumber(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "n/a";
  if (value <= 1 && value >= 0) return `${Math.round(value * 100)}%`;
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(2);
}

export function truncateText(value, length = 150) {
  if (isEmpty(value)) return "n/a";
  const text = String(value).trim().replace(/\s+/g, " ");
  return text.length <= length ? text : `${text.slice(0, length).trim()}...`;
}

export function previewText(value, length = 210) {
  if (isEmpty(value)) return { text: "n/a", truncated: false };
  const text = String(value).trim().replace(/\s+/g, " ");
  if (text.length <= length) return { text, truncated: false };
  const slice = text.slice(0, length + 1);
  const lastSpace = slice.lastIndexOf(" ");
  const safeCut = lastSpace > Math.floor(length * 0.65) ? lastSpace : length;
  return { text: `${text.slice(0, safeCut).trim()}…`, truncated: true };
}

export function truncateMiddle(value, head = 10, tail = 8) {
  if (isEmpty(value)) return "n/a";
  const text = String(value);
  return text.length <= head + tail + 3
    ? text
    : `${text.slice(0, head)}...${text.slice(-tail)}`;
}

export function safeRate(summary) {
  if (!summary?.total_cases) return 0;
  return summary.success_rate || 0;
}

// ── Tone helpers ──────────────────────────────────────────────────────────────

export function toneForStatus(status) {
  if (status === "completed") return "safe";
  if (status === "running") return "info";
  if (status === "failed") return "danger";
  if (status === "queued") return "warning";
  return "neutral";
}

export function toneForOutcome(value) {
  if (value === "success") return "danger";
  if (value === "blocked" || value === "no_success") return "safe";
  if (value === "partial") return "warning";
  return "neutral";
}

export function toneForAction(value) {
  if (value === "block") return "danger";
  if (value === "redact" || value === "escalate" || value === "safe_rewrite")
    return "warning";
  if (value === "allow") return "safe";
  return "neutral";
}

export function toneForSeverity(value) {
  if (value === "critical" || value === "high") return "danger";
  if (value === "medium") return "warning";
  if (value === "low") return "safe";
  return "neutral";
}

// ── Gate / verdict helpers ────────────────────────────────────────────────────

export function getDryRunMeta(verdict) {
  const meta = verdict?.detector_results?.dry_run;
  if (!meta || typeof meta !== "object" || meta.enabled !== true) return null;
  return meta;
}

export function getGateActionLabel(verdict) {
  const action = verdict?.action || "allow";
  const dryRunMeta = getDryRunMeta(verdict);
  if (
    dryRunMeta &&
    action === "allow" &&
    dryRunMeta.original_action &&
    dryRunMeta.original_action !== "allow"
  ) {
    return "Allow (dry-run)";
  }
  return formatLabel(action);
}

export function getGateActionTone(verdict) {
  const dryRunMeta = getDryRunMeta(verdict);
  if (
    dryRunMeta &&
    verdict?.action === "allow" &&
    dryRunMeta.original_action &&
    dryRunMeta.original_action !== "allow"
  ) {
    return "info";
  }
  return toneForAction(verdict?.action);
}

export function labelForOutcome(value) {
  if (value === "success") return "Succeeded";
  if (value === "blocked" || value === "no_success") return "Model Refused";
  if (value === "partial") return "Partial";
  return formatLabel(value || "pending");
}

export function buildTurnBadgeLabels(entry) {
  const severity = formatLabel(entry?.verdict?.severity || "low");
  const objective = labelForOutcome(
    entry?.event?.objective_scorer?.label || entry?.event?.outcome
  );
  return {
    severityShort: `Sev: ${severity}`,
    objectiveShort: `Obj: ${objective}`,
    severityLong: `Blue-team severity is ${severity}`,
    objectiveLong: `Red-team objective outcome is ${objective}`,
  };
}

// ── Narrative / display helpers ───────────────────────────────────────────────

export function runNarrative(status, turns) {
  if (!status) {
    return "Create a scenario, launch a run, and watch the attacker and guardrails interact in real time.";
  }
  if (status.status === "queued") {
    return "The run is queued and waiting for the backend worker.";
  }
  if (status.status === "running") {
    return `Live run in progress. ${status.turns_completed}/${status.max_turns} turns are captured and the current phase is ${formatLabel(status.current_phase)}.`;
  }
  if (status.status === "failed") {
    return status.summary || "The run failed before completion.";
  }
  return `Run completed with ${turns} recorded turn${turns === 1 ? "" : "s"}. Open any turn card to inspect what happened.`;
}

export function turnSummary(entry) {
  if (!entry) return "No explanation recorded.";
  return (
    entry.event?.objective_scorer?.reason ||
    entry.verdict?.reason ||
    "No explanation recorded."
  );
}

export function stageItems(entry) {
  const gateActionLabel = getGateActionLabel(entry?.verdict);
  return [
    { label: "Attack", value: entry?.event?.attacker_prompt ? "Ready" : "Pending" },
    {
      label: "Transform",
      value: entry?.event?.converter_steps?.length
        ? `${entry.event.converter_steps.length} step${entry.event.converter_steps.length === 1 ? "" : "s"}`
        : "Identity",
    },
    { label: "Target", value: entry?.event?.model_output ? "Captured" : "Pending" },
    {
      label: "Objective",
      value: formatLabel(
        entry?.event?.objective_scorer?.label || entry?.event?.outcome || "pending"
      ),
    },
    { label: "Blue team", value: gateActionLabel },
  ];
}

export function flattenBreakdown(map) {
  return Object.entries(map || {}).map(([key, value]) => ({ key, ...value }));
}

export function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function formatSignedCount(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "n/a";
  if (value === 0) return "0";
  return `${value > 0 ? "+" : ""}${value}`;
}

export function formatSignedPoints(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "n/a";
  const points = Math.round(value * 100);
  if (points === 0) return "0 pts";
  return `${points > 0 ? "+" : ""}${points} pts`;
}

export function toneForDelta(value) {
  if (typeof value !== "number" || Number.isNaN(value) || value === 0)
    return "neutral";
  return value > 0 ? "safe" : "danger";
}

export function selectState(value, options) {
  if (isEmpty(value)) return PRESET_PLACEHOLDER;
  return options.includes(value) ? value : CUSTOM_OPTION;
}
