import React, { useState } from "react";
import { AlertOctagon, Sliders, ShieldAlert, CheckCircle, RefreshCw } from "lucide-react";

export default function DisruptionControls({ 
  onRunOptimization, 
  onTriggerDisruption, 
  activeDisruptions,
  isOptimizing 
}) {
  // Procurement parameters state
  const [volume, setVolume] = useState("5 million barrels");
  const [deadline, setDeadline] = useState("15 days");
  const [crudeType, setCrudeType] = useState("medium sour crude");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [targetRefinery, setTargetRefinery] = useState("");

  const refineries = [
    "Jamnagar", 
    "Mumbai HPCL/BPCL", 
    "Paradip IOCL", 
    "Kochi BPCL", 
    "Visakhapatnam HPCL", 
    "Panipat IOCL", 
    "Chennai CPCL"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    onRunOptimization({
      required_volume: volume,
      deadline: deadline,
      preferred_crude: crudeType,
      risk_level: riskLevel,
      target_refinery: targetRefinery || null
    });
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Simulation Scenario Trigger Panel */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
        <h3 className="font-semibold text-xs text-slate-300 tracking-wider uppercase font-mono border-b border-cyber-border pb-2 mb-4 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-500" />
          DISRUPTION SCENARIO INJECTOR
        </h3>

        <div className="flex flex-col gap-3">
          <button
            onClick={() => onTriggerDisruption("Strait of Hormuz partial blockage")}
            className="flex items-center justify-between p-3 rounded-lg border border-red-950 bg-red-950 bg-opacity-20 hover:bg-opacity-40 transition text-left text-xs"
          >
            <div>
              <span className="font-semibold text-red-400 block font-mono">STrait of Hormuz block</span>
              <span className="text-[10px] text-slate-400">Blocks Persian Gulf shipments (Saudi & Iraq routes)</span>
            </div>
            <AlertOctagon className="w-5 h-5 text-red-500 flex-shrink-0" />
          </button>

          <button
            onClick={() => onTriggerDisruption("Arabian Sea Cyclone")}
            className="flex items-center justify-between p-3 rounded-lg border border-amber-950 bg-amber-950 bg-opacity-20 hover:bg-opacity-40 transition text-left text-xs"
          >
            <div>
              <span className="font-semibold text-amber-400 block font-mono">Arabian Sea Cyclone</span>
              <span className="text-[10px] text-slate-400">Halts West Coast ports, spikes wave height to 5.5m</span>
            </div>
            <AlertOctagon className="w-5 h-5 text-amber-500 flex-shrink-0" />
          </button>

          <button
            onClick={() => onTriggerDisruption("Mundra Congestion Strike")}
            className="flex items-center justify-between p-3 rounded-lg border border-blue-950 bg-blue-950 bg-opacity-20 hover:bg-opacity-40 transition text-left text-xs"
          >
            <div>
              <span className="font-semibold text-sky-400 block font-mono">Mundra Congestion Spike</span>
              <span className="text-[10px] text-slate-400">Spikes waiting times to 52 hours at Mundra port</span>
            </div>
            <AlertOctagon className="w-5 h-5 text-sky-400 flex-shrink-0" />
          </button>

          {activeDisruptions.length > 0 ? (
            <button
              onClick={() => onTriggerDisruption("Clear Disruptions")}
              className="flex items-center justify-center gap-2 p-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 transition text-slate-900 text-xs font-bold font-mono mt-2"
            >
              <RefreshCw className="w-4 h-4" />
              CLEAR ACTIVE DISRUPTIONS
            </button>
          ) : (
            <div className="p-3 text-center border border-dashed border-slate-800 rounded-lg text-[10px] text-slate-500 font-mono">
              <CheckCircle className="w-4 h-4 text-emerald-500 mx-auto mb-1 inline-block" />
              <span>SUPPLY CHAIN: STANDBY / NOMINAL STATUS</span>
            </div>
          )}
        </div>
      </div>

      {/* Procurement Optimization Input Panel */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
        <h3 className="font-semibold text-xs text-slate-300 tracking-wider uppercase font-mono border-b border-cyber-border pb-2 mb-4 flex items-center gap-2">
          <Sliders className="w-4 h-4 text-cyan-400" />
          PROCUREMENT REQUIREMENT
        </h3>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-xs">
          {/* Volume */}
          <div>
            <label className="block text-[10px] text-slate-400 font-mono uppercase mb-1.5">
              Required Volume
            </label>
            <input
              type="text"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              placeholder="e.g. 5 million barrels"
              className="w-full bg-slate-950 border border-cyber-border rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-[10px] text-slate-400 font-mono uppercase mb-1.5">
              Procurement Deadline
            </label>
            <input
              type="text"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              placeholder="e.g. 15 days"
              className="w-full bg-slate-950 border border-cyber-border rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
          </div>

          {/* Preferred Crude Type */}
          <div>
            <label className="block text-[10px] text-slate-400 font-mono uppercase mb-1.5">
              Preferred Crude Grade
            </label>
            <select
              value={crudeType}
              onChange={(e) => setCrudeType(e.target.value)}
              className="w-full bg-slate-950 border border-cyber-border rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="medium sour crude">Medium Sour Crude (Saudi/Russia type)</option>
              <option value="light sweet crude">Light Sweet Crude (US/Nigeria/UAE type)</option>
              <option value="heavy sour crude">Heavy Sour Crude (Iraq/Venezuela type)</option>
              <option value="medium sweet crude">Medium Sweet Crude (Brazil type)</option>
            </select>
          </div>

          {/* Target Refinery */}
          <div>
            <label className="block text-[10px] text-slate-400 font-mono uppercase mb-1.5">
              Destination Refinery
            </label>
            <select
              value={targetRefinery}
              onChange={(e) => setTargetRefinery(e.target.value)}
              className="w-full bg-slate-950 border border-cyber-border rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="">-- ALL COMPATIBLE REFINERIES --</option>
              {refineries.map((ref) => (
                <option key={ref} value={ref}>{ref}</option>
              ))}
            </select>
          </div>

          {/* Risk Level */}
          <div>
            <label className="block text-[10px] text-slate-400 font-mono uppercase mb-1.5">
              Risk Tolerance
            </label>
            <div className="grid grid-cols-3 gap-2">
              {["low", "medium", "high"].map((r) => (
                <button
                  type="button"
                  key={r}
                  onClick={() => setRiskLevel(r)}
                  className={`py-1.5 border rounded uppercase font-mono font-semibold text-[10px] transition ${
                    riskLevel === r
                      ? "bg-cyan-500 bg-opacity-20 text-cyan-400 border-cyan-500"
                      : "bg-slate-950 border-cyber-border text-slate-400 hover:border-slate-700"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isOptimizing}
            className="w-full bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-700 text-slate-950 font-bold py-2.5 px-4 rounded transition font-mono tracking-wider mt-2 flex items-center justify-center gap-2"
          >
            {isOptimizing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                OPTIMIZING ROUTE MATRIX...
              </>
            ) : (
              "EXECUTE OPTIMIZATION"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
