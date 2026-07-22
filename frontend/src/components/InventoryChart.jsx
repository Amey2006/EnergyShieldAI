import React from "react";

const LABELS = {
  crude_stocks_kbbl: "US Crude Stocks (kbbl)",
  refinery_utilization_pct: "Refinery Utilization (%)",
  crude_imports_kbbl_day: "US Crude Imports (kbbl/day)",
  crude_exports_kbbl_day: "US Crude Exports (kbbl/day)",
};

export default function InventoryChart({ inventory }) {
  const metrics = inventory?.metrics;

  if (!metrics || Object.keys(metrics).length === 0) {
    return (
      <div className="empty-state">
        {inventory?.error === "EIA_API_KEY not set"
          ? "Add EIA_API_KEY to .env to enable this panel"
          : "No inventory data yet — start orchestrator.py"}
      </div>
    );
  }

  return (
    <div>
      {Object.entries(metrics).map(([key, data]) => (
        <div className="stat-row" key={key}>
          <span className="label">{LABELS[key] || key}</span>
          <span className="value">
            {data ? `${data.value} (${data.period})` : "—"}
          </span>
        </div>
      ))}
    </div>
  );
}
