import React, { useState, useEffect } from "react";
import DigitalTwinMap from "./components/DigitalTwinMap";
import AgentLogTerminal from "./components/AgentLogTerminal";
import OptimizationResults from "./components/OptimizationResults";
import DisruptionControls from "./components/DisruptionControls";
import { ShieldCheck, Anchor, ShieldAlert, Award, FileText, Search, BookOpen, AlertCircle } from "lucide-react";

export default function App() {
  const [mapData, setMapData] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(0);
  const [activeDisruptions, setActiveDisruptions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [resilienceIndex, setResilienceIndex] = useState(92);
  
  // Vector search state
  const [vectorQuery, setVectorQuery] = useState("");
  const [vectorResults, setVectorResults] = useState([]);
  const [isSearchingVector, setIsSearchingVector] = useState(false);

  // Fetch initial digital twin map layers
  const fetchDigitalTwin = async () => {
    try {
      const resp = await fetch("/api/digital-twin");
      if (resp.ok) {
        const data = await resp.json();
        setMapData(data);
        setActiveDisruptions(data.active_disruptions || []);
        
        // Dynamically compute resilience index based on active blockages and port waiting times
        let baseResilience = 94;
        if (data.blocked_nodes.includes("Strait of Hormuz")) {
          baseResilience -= 35;
        }
        const activeAlerts = data.active_disruptions.length;
        baseResilience -= activeAlerts * 8;
        setResilienceIndex(Math.max(15, baseResilience));
      }
    } catch (err) {
      console.error("Error loading digital twin map layers:", err);
    }
  };

  useEffect(() => {
    fetchDigitalTwin();
  }, []);

  // Run Route Optimization
  const handleRunOptimization = async (params) => {
    setIsOptimizing(true);
    setLogs(["Supervisor: Received optimization request. Initializing sub-agent cluster..."]);
    try {
      const resp = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      if (resp.ok) {
        const data = await resp.json();
        setOptimizationResult(data);
        setLogs(data.logs || []);
        setSelectedRouteIndex(0);
      } else {
        const errData = await resp.json();
        setLogs([`Supervisor: Optimization error - ${errData.detail || "Server failed to process route request."}`]);
      }
    } catch (err) {
      setLogs(["Supervisor: Connection failed. Verify FastAPI backend server is active."]);
    } finally {
      setIsOptimizing(false);
    }
  };

  // Trigger Disruption Event
  const handleTriggerDisruption = async (scenarioName) => {
    setIsOptimizing(true);
    try {
      const resp = await fetch("/api/simulate-disruption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: scenarioName }),
      });
      if (resp.ok) {
        await fetchDigitalTwin();
        // Immediately run an optimization check with the new blockage
        handleRunOptimization({
          required_volume: "5 million barrels",
          deadline: "15 days",
          preferred_crude: "medium sour crude",
          risk_level: "medium"
        });
      }
    } catch (err) {
      console.error("Disruption simulator error:", err);
    } finally {
      setIsOptimizing(false);
    }
  };

  // Vector Search Knowledge Base
  const handleVectorSearch = async (e) => {
    if (e) e.preventDefault();
    if (!vectorQuery.trim()) return;
    setIsSearchingVector(true);
    try {
      const resp = await fetch("/api/vector-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: vectorQuery, top_k: 2 }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setVectorResults(data.results || []);
      }
    } catch (err) {
      console.error("Vector search failed:", err);
    } finally {
      setIsSearchingVector(false);
    }
  };

  const currentRoute = optimizationResult?.top_5_alternatives?.[selectedRouteIndex];

  return (
    <div className="min-h-screen bg-cyber-dark text-slate-100 flex flex-col p-4 md:p-6 font-sans">
      
      {/* Executive Command Header */}
      <header className="flex flex-col lg:flex-row items-start lg:items-center justify-between border-b border-cyber-border pb-4 mb-6 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="bg-cyan-500 text-slate-950 text-[10px] font-bold px-2 py-0.5 rounded uppercase font-mono tracking-wider">
              Module 2 - Active Routing
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] text-slate-400 font-mono">SUPPLY CHAIN DIGITAL TWIN</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-sans">
            AI Energy Logistics Optimization Agent
          </h1>
        </div>

        {/* Global Supply Chain KPI Summary */}
        <div className="flex flex-wrap items-center gap-4 lg:gap-6 bg-slate-900 border border-cyber-border rounded-xl p-3 shadow-lg">
          {/* Resilience Index */}
          <div className="flex items-center gap-3 pr-4 border-r border-slate-800">
            <div className="relative flex items-center justify-center">
              <span className={`text-xl font-bold font-mono ${resilienceIndex > 70 ? 'text-emerald-400' : resilienceIndex > 45 ? 'text-yellow-400' : 'text-red-400'}`}>
                {resilienceIndex}%
              </span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 font-mono block uppercase">Resilience Index</span>
              <span className="text-xs font-semibold text-slate-300">
                {resilienceIndex > 70 ? "SECURE STATUS" : resilienceIndex > 45 ? "ELEVATED RISK" : "CRITICAL SHIELD"}
              </span>
            </div>
          </div>

          {/* Active alerts */}
          <div className="flex items-center gap-2.5 pr-4 border-r border-slate-800">
            <ShieldAlert className={`w-5 h-5 ${activeDisruptions.length > 0 ? "text-red-500 animate-bounce" : "text-slate-500"}`} />
            <div>
              <span className="text-[9px] text-slate-500 font-mono block uppercase">Active Alerts</span>
              <span className="text-xs font-bold font-mono text-slate-300">
                {activeDisruptions.length} Disruptions
              </span>
            </div>
          </div>

          {/* Sourced tank capacity */}
          <div className="flex items-center gap-2.5">
            <Anchor className="w-5 h-5 text-cyan-400" />
            <div>
              <span className="text-[9px] text-slate-500 font-mono block uppercase">Base Rate Average</span>
              <span className="text-xs font-bold font-mono text-slate-300">
                {currentRoute ? `$${currentRoute.cost_per_barrel}/bbl` : "$0.00/bbl"}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid Content */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* Left Columns - Controls & Knowledge Base (3/12 width) */}
        <div className="xl:col-span-3 flex flex-col gap-6">
          <DisruptionControls 
            onRunOptimization={handleRunOptimization}
            onTriggerDisruption={handleTriggerDisruption}
            activeDisruptions={activeDisruptions}
            isOptimizing={isOptimizing}
          />

          {/* Vector Database SOP Search */}
          <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
            <h3 className="font-semibold text-xs text-slate-300 tracking-wider uppercase font-mono border-b border-cyber-border pb-2 mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-emerald-400" />
              MARITIME SOP SEARCH (VECTOR DB)
            </h3>
            
            <form onSubmit={handleVectorSearch} className="flex gap-2 mb-3">
              <input
                type="text"
                value={vectorQuery}
                onChange={(e) => setVectorQuery(e.target.value)}
                placeholder="Search SOP (e.g. Hormuz block)"
                className="flex-1 bg-slate-950 border border-cyber-border rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              />
              <button 
                type="submit"
                disabled={isSearchingVector}
                className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 p-2 rounded flex items-center justify-center transition"
              >
                <Search className="w-4 h-4" />
              </button>
            </form>

            <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
              {vectorResults.length > 0 ? (
                vectorResults.map((res, idx) => (
                  <div key={idx} className="bg-slate-950 border border-slate-800 p-2 rounded text-xs">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-1 mb-1.5">
                      <span className="font-bold text-[10px] text-emerald-400 truncate max-w-[80%] font-mono">
                        {res.title}
                      </span>
                      <span className="text-[9px] bg-slate-900 border border-slate-800 text-slate-500 px-1 rounded font-mono">
                        {(res.score * 100).toFixed(0)}% Match
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 leading-relaxed font-sans">{res.content}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-[10px] text-slate-600 font-mono">
                  <span>Enter query to retrieve vector guidelines from repository knowledge base.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Middle Columns - Digital Twin Map & Terminal Console (6/12 width) */}
        <div className="xl:col-span-6 flex flex-col gap-6">
          <div className="bg-cyber-card border border-cyber-border rounded-xl p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-cyber-border pb-2">
              <h3 className="font-semibold text-xs text-slate-300 tracking-wider uppercase font-mono flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                DIGITAL TWIN ROUTING CANVAS
              </h3>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] bg-slate-900 text-slate-400 px-2 py-0.5 rounded font-mono border border-slate-800">
                  Layers: Ship lanes, Tankers, Refineries
                </span>
              </div>
            </div>
            
            {/* Visual Leaflet Map */}
            <div className="w-full relative h-[450px]">
              {mapData ? (
                <DigitalTwinMap 
                  mapData={mapData} 
                  recommendedRoutePath={currentRoute?.route_path || []} 
                />
              ) : (
                <div className="w-full h-full bg-slate-950 rounded-xl flex items-center justify-center border border-cyber-border text-slate-500 text-sm font-mono animate-pulse">
                  Initializing Cartographic Engine...
                </div>
              )}
            </div>
          </div>

          {/* Sub-agent multi-step terminal console */}
          <AgentLogTerminal logs={logs} isRunning={isOptimizing} />
        </div>

        {/* Right Columns - Optimization Results & Executive Briefing (3/12 width) */}
        <div className="xl:col-span-3 flex flex-col gap-6">
          
          {/* Top 5 list rankings */}
          {optimizationResult && (
            <OptimizationResults 
              results={optimizationResult.top_5_alternatives} 
              selectedIndex={selectedRouteIndex}
              onSelectIndex={setSelectedRouteIndex}
            />
          )}

          {/* Executive Explainability report card */}
          <div className="bg-cyber-card border border-cyber-border rounded-xl p-4">
            <h3 className="font-semibold text-xs text-slate-300 tracking-wider uppercase font-mono border-b border-cyber-border pb-2 mb-4 flex items-center gap-2">
              <Award className="w-4 h-4 text-cyan-400" />
              EXECUTIVE PROCUREMENT DECISION
            </h3>

            {optimizationResult ? (
              <div className="flex flex-col gap-4">
                {/* Visual scorecard */}
                <div className="bg-slate-950 border border-slate-900 p-3 rounded-lg flex flex-col gap-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-mono">SUPPLIER:</span>
                    <span className="font-bold text-white uppercase">{optimizationResult.recommended_supplier}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-mono">DELIVERY ETA:</span>
                    <span className="font-bold text-cyan-400 font-mono">{optimizationResult.estimated_delivery_time}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-mono">LOGISTICS COST:</span>
                    <span className="font-bold text-emerald-400 font-mono">{optimizationResult.estimated_cost}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-mono">COMPOSITE RISK:</span>
                    <span className="font-bold text-red-400 font-mono">{optimizationResult.risk_score}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-mono">CONFIDENCE RATIO:</span>
                    <span className="font-bold text-cyan-400 font-mono">{optimizationResult.confidence_score}</span>
                  </div>
                </div>

                {/* Natural language explanation box */}
                <div className="bg-slate-950 border border-slate-900 p-3 rounded-lg text-xs leading-relaxed max-h-[300px] overflow-y-auto pr-1 text-slate-300">
                  <h4 className="font-bold text-slate-400 mb-2 border-b border-slate-800 pb-1 uppercase font-mono text-[10px]">
                    ARCHITECT REASONING
                  </h4>
                  <div 
                    className="prose prose-invert prose-xs font-sans space-y-2"
                    dangerouslySetInnerHTML={{ 
                      __html: optimizationResult.reasoning
                        .replace(/\n/g, "<br />")
                        .replace(/\* \*\*(.*?)\*\*/g, "<strong>$1</strong>")
                        .replace(/\*(.*?)\*/g, "<em>$1</em>")
                        .replace(/\* (.*?)/g, "• $1") 
                    }}
                  />
                </div>
              </div>
            ) : (
              <div className="p-6 border border-dashed border-slate-800 rounded-lg text-center text-xs text-slate-500 font-mono flex flex-col gap-2">
                <AlertCircle className="w-6 h-6 mx-auto text-slate-600 animate-bounce" />
                <span>Submit procurement request or inject a blockage to trigger AI architect synthesis.</span>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
