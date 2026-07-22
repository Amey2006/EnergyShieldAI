import React, { useEffect, useState, useCallback } from "react";
import { getDashboard } from "./api";
import RiskGauge from "./components/RiskGauge";
import PriceChart from "./components/PriceChart";
import InventoryChart from "./components/InventoryChart";
import NewsFeed from "./components/NewsFeed";
import VesselMap from "./components/VesselMap";
import NewsTestInput from "./components/NewsTestInput";

const REFRESH_MS = 60 * 1000; // auto-refresh every 1 minute, as requested

export default function App() {
  const [data, setData] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const result = await getDashboard();
      setData(result);
      setLastRefreshed(new Date());
    } catch (e) {
      console.error("Dashboard refresh failed:", e.message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, REFRESH_MS);
    return () => clearInterval(interval);
  }, [refresh]);

  const recommendation = data?.recommendation?.recommendation;
  const corridorRisk =
    data?.prediction?.corridor_disruption_probability ||
    data?.news?.aggregate?.disruption_probability_by_corridor;

  return (
    <div className="app-shell">
      <div className="topbar">
        <div>
          <h1>Energy Supply Chain Resilience</h1>
          <div className="subtitle">India crude oil corridor monitoring</div>
        </div>
        <div className="live-indicator">
          <span className="live-dot" />
          {lastRefreshed
            ? `Updated ${lastRefreshed.toLocaleTimeString()} · refreshes every 60s`
            : "Connecting..."}
        </div>
      </div>

      <div className="grid">
        <div className="panel span-12">
          <h2>Corridor Disruption Probability</h2>
          <RiskGauge corridorRisk={corridorRisk} />
        </div>

        <div className="panel span-8">
          <h2>Brent Price Forecast (ARIMA + GARCH)</h2>
          <PriceChart prediction={data?.prediction} />
        </div>

        <div className="panel span-4">
          <h2>Recommendation Agent</h2>
          {recommendation ? (
            <>
              <div className="stat-row">
                <span className="label">Risk level</span>
                <span className="value">{recommendation.risk_level}</span>
              </div>
              <div className="stat-row">
                <span className="label">Primary corridor</span>
                <span className="value">{recommendation.primary_corridor_of_concern}</span>
              </div>
              <p style={{ fontSize: 12.5, color: "#8b98a3" }}>{recommendation.summary}</p>
              {recommendation.recommended_actions?.map((a, i) => (
                <div className="recommendation-box" key={i}>
                  <strong>{a.action}</strong> <span style={{ color: "#8b98a3" }}>({a.urgency})</span>
                  <div style={{ marginTop: 4 }}>{a.rationale}</div>
                </div>
              ))}
            </>
          ) : (
            <div className="empty-state">No recommendation yet — start orchestrator.py</div>
          )}
        </div>

        <div className="panel span-6">
          <h2>Vessel &amp; Chokepoint Map</h2>
          <VesselMap shipping={data?.shipping} />
        </div>

        <div className="panel span-3">
          <h2>US Inventory (EIA)</h2>
          <InventoryChart inventory={data?.inventory} />
        </div>

        <div className="panel span-3">
          <h2>Test: Paste News Paragraph</h2>
          <NewsTestInput />
        </div>

        <div className="panel span-12">
          <h2>Live News Feed</h2>
          <NewsFeed news={data?.news} />
        </div>
      </div>
    </div>
  );
}
