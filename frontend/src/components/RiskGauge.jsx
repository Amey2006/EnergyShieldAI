import React from "react";

const CORRIDOR_LABELS = {
  hormuz: "Strait of Hormuz",
  red_sea: "Red Sea",
  opec: "OPEC+",
  russia: "Russia / Urals",
  general: "General",
};

function riskClass(value) {
  if (value >= 0.6) return "risk-high";
  if (value >= 0.3) return "risk-moderate";
  return "risk-low";
}

export default function RiskGauge({ corridorRisk }) {
  const entries = Object.entries(corridorRisk || {});

  if (entries.length === 0) {
    return <div className="empty-state">No corridor risk data yet — start orchestrator.py</div>;
  }

  return (
    <div className="annunciator-strip">
      {entries.map(([corridor, value]) => (
        <div key={corridor} className={`annunciator-cell ${riskClass(value)}`}>
          <div className="corridor-name">{CORRIDOR_LABELS[corridor] || corridor}</div>
          <div className="corridor-value">{Math.round(value * 100)}%</div>
        </div>
      ))}
    </div>
  );
}
