import React from "react";
import { ShieldCheck, Calendar, DollarSign, Activity, ChevronRight, Droplets, Wind, Navigation, Ship, Database } from "lucide-react";

export default function OptimizationResults({ results, selectedIndex, onSelectIndex }) {
  if (!results || results.length === 0) return null;

  return (
    <div className="flex flex-col gap-4">
      <h3 className="font-semibold text-sm text-slate-300 tracking-wider uppercase font-mono border-b border-cyber-border pb-2">
        RANKED OPTIMAL PATHWAYS
      </h3>

      <div className="flex flex-col gap-3">
        {results.map((route, idx) => {
          const isSelected = selectedIndex === idx;
          const isBest = idx === 0;

          return (
            <div
              key={idx}
              onClick={() => onSelectIndex(idx)}
              className={`p-3 rounded-xl border transition-all duration-200 cursor-pointer flex flex-col gap-2 ${
                isSelected
                  ? "bg-slate-900 border-cyan-500 shadow-[0_0_12px_rgba(56,189,248,0.25)]"
                  : "bg-cyber-card border-cyber-border hover:border-slate-700"
              }`}
            >
              {/* Header Info */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded font-bold ${
                    isBest 
                      ? "bg-cyan-500 bg-opacity-20 text-cyan-400 border border-cyan-500" 
                      : "bg-slate-800 text-slate-400"
                  }`}>
                    {isBest ? "Rank #1 - RECOMMENDED" : `Rank #${idx + 1}`}
                  </span>
                  <span className="text-xs font-semibold text-slate-300">
                    {route.supplier} → {route.refinery}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-xs text-slate-500 font-mono">Score:</span>
                  <span className={`text-xs font-bold font-mono ${isBest ? "text-cyan-400" : "text-slate-300"}`}>
                    {route.final_score}/100
                  </span>
                </div>
              </div>

              {/* Transit Path Display */}
              <div className="text-[11px] text-slate-400 font-mono flex items-center gap-1 bg-slate-950 p-1.5 rounded border border-slate-900">
                <Navigation className="w-3.5 h-3.5 text-cyan-500 flex-shrink-0" />
                <span className="truncate">{route.route_path_display}</span>
              </div>

              {/* High-level KPIs */}
              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="bg-slate-950 bg-opacity-50 p-1.5 rounded border border-slate-900">
                  <span className="block text-[9px] text-slate-500 font-mono">COST</span>
                  <span className="text-xs font-bold font-mono text-emerald-400">${route.total_cost_million_usd}M</span>
                </div>
                <div className="bg-slate-950 bg-opacity-50 p-1.5 rounded border border-slate-900">
                  <span className="block text-[9px] text-slate-500 font-mono">TRANSIT</span>
                  <span className="text-xs font-bold font-mono text-slate-300">{route.transit_time_days} Days</span>
                </div>
                <div className="bg-slate-950 bg-opacity-50 p-1.5 rounded border border-slate-900">
                  <span className="block text-[9px] text-slate-500 font-mono">RISK</span>
                  <span className={`text-xs font-bold font-mono ${route.risk_score > 50 ? 'text-red-400' : 'text-slate-300'}`}>
                    {route.risk_score}/100
                  </span>
                </div>
                <div className="bg-slate-950 bg-opacity-50 p-1.5 rounded border border-slate-900">
                  <span className="block text-[9px] text-slate-500 font-mono">CONFIDENCE</span>
                  <span className="text-xs font-bold font-mono text-cyan-400">{route.confidence_score}%</span>
                </div>
              </div>

              {/* Sub-Agent Breakdown Panel (Shown when selected) */}
              {isSelected && (
                <div className="mt-2 border-t border-slate-800 pt-3 grid grid-cols-2 gap-3 text-xs text-slate-400">
                  {/* Port Info */}
                  <div className="flex items-start gap-2 bg-slate-950 p-2 rounded border border-slate-900">
                    <Database className="w-4 h-4 text-brand-400 mt-0.5" />
                    <div>
                      <h5 className="font-semibold text-slate-300 text-[10px] uppercase font-mono">Port Suitability</h5>
                      <p className="text-[10px] mt-0.5">Port: {route.destination_port}</p>
                      <p className="text-[10px]">Queue: {route.sub_agent_reports.port_intelligence.waiting_vessels} vessels</p>
                      <p className="text-[10px]">Congestion: {route.sub_agent_reports.port_intelligence.congestion_score}/100</p>
                    </div>
                  </div>

                  {/* Refinery Info */}
                  <div className="flex items-start gap-2 bg-slate-950 p-2 rounded border border-slate-900">
                    <Droplets className="w-4 h-4 text-emerald-400 mt-0.5" />
                    <div>
                      <h5 className="font-semibold text-slate-300 text-[10px] uppercase font-mono">Crude Blending</h5>
                      <p className="text-[10px] mt-0.5">API: {route.sub_agent_reports.refinery_compatibility.api_gravity}</p>
                      <p className="text-[10px]">Sulfur: {route.sub_agent_reports.refinery_compatibility.sulfur_content}</p>
                      <p className="text-[10px] font-medium text-emerald-400">Match: {route.refinery_compatibility}%</p>
                    </div>
                  </div>

                  {/* Weather Info */}
                  <div className="flex items-start gap-2 bg-slate-950 p-2 rounded border border-slate-900">
                    <Wind className="w-4 h-4 text-purple-400 mt-0.5" />
                    <div>
                      <h5 className="font-semibold text-slate-300 text-[10px] uppercase font-mono">Weather Risk</h5>
                      <p className="text-[10px] mt-0.5">Max risk: {route.weather_risk}/100</p>
                      <p className="text-[10px]">Route: {route.sub_agent_reports.route_optimization.distance_nm} NM</p>
                      <p className="text-[10px] text-slate-500">Source: Open-Meteo API</p>
                    </div>
                  </div>

                  {/* Tanker Info */}
                  <div className="flex items-start gap-2 bg-slate-950 p-2 rounded border border-slate-900">
                    <Ship className="w-4 h-4 text-cyan-400 mt-0.5" />
                    <div>
                      <h5 className="font-semibold text-slate-300 text-[10px] uppercase font-mono">Chartered Fleet</h5>
                      <p className="text-[10px] mt-0.5">ETA: {route.sub_agent_reports.tanker_availability.eta_days} days</p>
                      <p className="text-[10px]">Vessels: {route.sub_agent_reports.tanker_availability.available_count} active</p>
                      <p className="text-[10px]">Rate: ${route.cost_per_barrel}/bbl total</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
