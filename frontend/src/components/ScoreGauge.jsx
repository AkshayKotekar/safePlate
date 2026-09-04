import React from "react";

const STATUS_COLOR = {
  EXCELLENT: "#33d17a",
  SAFE: "#3ea6ff",
  WARNING: "#f2a33c",
  UNHYGIENIC: "#e05252",
};

function colorForScore(score) {
  if (score >= 90) return STATUS_COLOR.EXCELLENT;
  if (score >= 70) return STATUS_COLOR.SAFE;
  if (score >= 50) return STATUS_COLOR.WARNING;
  return STATUS_COLOR.UNHYGIENIC;
}

export default function ScoreGauge({ score, size = 96, strokeWidth = 8, label }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const offset = circumference * (1 - pct);
  const color = colorForScore(score);

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--panel2)" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
        <text
          x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
          transform={`rotate(90 ${size / 2} ${size / 2})`}
          style={{ fontSize: size * 0.28, fontWeight: 800, fill: "var(--text)", fontFamily: "Inter, sans-serif" }}
        >
          {Math.round(score)}
        </text>
      </svg>
      {label && <div style={{ fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>{label}</div>}
    </div>
  );
}
