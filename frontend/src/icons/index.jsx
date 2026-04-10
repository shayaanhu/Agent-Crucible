import React from "react";
// All SVG icon components used across the app.
// They share a common IconBase wrapper for consistent sizing and stroke handling.

function IconBase({
  size = 16,
  strokeWidth = 1.8,
  className,
  style,
  children,
  viewBox = "0 0 24 24",
  ...props
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={style}
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export function GraduationCap(props) {
  return (
    <IconBase {...props}>
      <path d="M2 9 12 4l10 5-10 5-10-5Z" />
      <path d="M6 11.5V16c0 1.6 2.7 3 6 3s6-1.4 6-3v-4.5" />
      <path d="M22 9v6" />
    </IconBase>
  );
}

export function Building2(props) {
  return (
    <IconBase {...props}>
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <path d="M8 7h.01M12 7h.01M16 7h.01M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01" />
      <path d="M10 21v-3h4v3" />
    </IconBase>
  );
}

export function Heart(props) {
  return (
    <IconBase {...props}>
      <path d="M12 20s-7-4.6-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.4-7 10-7 10Z" />
    </IconBase>
  );
}

export function Headphones(props) {
  return (
    <IconBase {...props}>
      <path d="M4 13a8 8 0 0 1 16 0" />
      <rect x="3" y="12" width="4" height="8" rx="2" />
      <rect x="17" y="12" width="4" height="8" rx="2" />
      <path d="M7 20h10" />
    </IconBase>
  );
}

export function Code2(props) {
  return (
    <IconBase {...props}>
      <path d="m8 8-4 4 4 4" />
      <path d="m16 8 4 4-4 4" />
      <path d="m14 5-4 14" />
    </IconBase>
  );
}

export function Scale(props) {
  return (
    <IconBase {...props}>
      <path d="M12 4v16" />
      <path d="M7 7h10" />
      <path d="M4 21h16" />
      <path d="m7 7-3 6h6l-3-6Z" />
      <path d="m17 7-3 6h6l-3-6Z" />
    </IconBase>
  );
}

export function ArrowLeft(props) {
  return (
    <IconBase {...props}>
      <path d="M19 12H5" />
      <path d="m12 19-7-7 7-7" />
    </IconBase>
  );
}

export function X(props) {
  return (
    <IconBase {...props}>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </IconBase>
  );
}

export function Plus(props) {
  return (
    <IconBase {...props}>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </IconBase>
  );
}

export function PlayCircle(props) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="m10 8 6 4-6 4Z" fill="currentColor" stroke="none" />
    </IconBase>
  );
}

export function Sword(props) {
  return (
    <IconBase {...props}>
      <path d="m11 19-6-6" />
      <path d="m5 21-2-2" />
      <path d="m8 16-4 4" />
      <path d="M9.5 17.5 21 6V3h-3L6.5 14.5" />
    </IconBase>
  );
}

export function Terminal(props) {
  return (
    <IconBase {...props}>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="m7 9 3 3-3 3" />
      <path d="M13 15h3" />
    </IconBase>
  );
}

export function Crosshair(props) {
  return (
    <IconBase {...props}>
      <circle cx="12" cy="12" r="7" />
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
      <circle cx="12" cy="12" r="2" fill="currentColor" stroke="none" />
    </IconBase>
  );
}

export function BarChart3(props) {
  return (
    <IconBase {...props}>
      <path d="M18 20V10" />
      <path d="M12 20V4" />
      <path d="M6 20v-6" />
    </IconBase>
  );
}

export function ShieldIcon(props) {
  return (
    <IconBase {...props}>
      <path d="M12 3 5 6v5c0 5 3.4 8.4 7 10 3.6-1.6 7-5 7-10V6l-7-3Z" />
      <path d="M12 8v8" />
      <path d="M8.5 12H15.5" />
    </IconBase>
  );
}

export function Bot(props) {
  return (
    <IconBase {...props}>
      <rect x="5" y="8" width="14" height="10" rx="3" />
      <path d="M12 4v4" />
      <path d="M9 12h.01M15 12h.01" />
      <path d="M9 16h6" />
    </IconBase>
  );
}

export function ChevronRight(props) {
  return (
    <IconBase {...props}>
      <path d="m9 6 6 6-6 6" />
    </IconBase>
  );
}

export function ChevronUp(props) {
  return (
    <IconBase {...props}>
      <path d="m6 15 6-6 6 6" />
    </IconBase>
  );
}

export function ChevronDown(props) {
  return (
    <IconBase {...props}>
      <path d="m6 9 6 6 6-6" />
    </IconBase>
  );
}

export function Check(props) {
  return (
    <IconBase {...props}>
      <path d="m5 12 4 4L19 6" />
    </IconBase>
  );
}
