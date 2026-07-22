import React from "react";
import {
  ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from "recharts";

export default function PriceChart({ prediction }) {
  const daily = prediction?.daily_forecast;

  if (!daily || daily.length === 0) {
    return <div className="empty-state">No forecast yet — start orchestrator.py</div>;
  }

  return (
    <div>
      <div className="stat-row">
        <span className="label">Last actual Brent close</span>
        <span className="value">${prediction.last_actual_price}</span>
      </div>
      <div className="stat-row">
        <span className="label">Model</span>
        <span className="value">
          {prediction.methodology?.trend_model} + {prediction.methodology?.volatility_model}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={daily} margin={{ top: 16, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#232b32" />
          <XAxis dataKey="date" tick={{ fill: "#8b98a3", fontSize: 11 }} />
          <YAxis tick={{ fill: "#8b98a3", fontSize: 11 }} domain={["auto", "auto"]} />
          <Tooltip
            contentStyle={{ background: "#12171c", border: "1px solid #232b32", fontSize: 12 }}
            labelStyle={{ color: "#e8e6e1" }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area
            type="monotone" dataKey="upper_95" stroke="none" fill="#4cc9f0" fillOpacity={0.08}
            name="Upper 95% CI"
          />
          <Area
            type="monotone" dataKey="lower_95" stroke="none" fill="#0b0e11" fillOpacity={1}
            name="Lower 95% CI"
          />
          <Line
            type="monotone" dataKey="brent_forecast" stroke="#f5a623" strokeWidth={2}
            dot={{ r: 3 }} name="Brent forecast ($)"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
