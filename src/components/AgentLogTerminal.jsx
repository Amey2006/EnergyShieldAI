import React, { useEffect, useRef } from "react";
import { Terminal, ShieldAlert } from "lucide-react";

export default function AgentLogTerminal({ logs, isRunning }) {
  const terminalEndRef = useRef(null);

  // Automatically scroll to bottom when new logs arrive
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  return (
    <div className="w-full bg-cyber-dark border border-cyber-border rounded-xl p-4 flex flex-col h-[300px]">
      <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-3">
        <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs">
          <Terminal className="w-4 h-4 animate-pulse" />
          <span>MULTI-AGENT ORCHESTRATION CONSOLE</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-full ${isRunning ? 'bg-cyan-500 animate-ping' : 'bg-slate-500'}`} />
          <span className="text-[10px] text-slate-400 font-mono">
            {isRunning ? "PROCESSING LOGISTICS GRAPH" : "STANDBY"}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto font-mono text-[11px] space-y-1.5 pr-2 scrollbar-thin scrollbar-track-slate-900 scrollbar-thumb-slate-800 text-slate-300">
        {logs && logs.length > 0 ? (
          logs.map((log, idx) => {
            // Highlight supervisor logs
            const isSupervisor = log.startsWith("Supervisor:");
            const isDisqualified = log.includes("Disqualified") || log.includes("failed");
            const isEvaluation = log.startsWith("Evaluated");
            
            let colorClass = "text-slate-300";
            if (isSupervisor) colorClass = "text-cyan-400 font-semibold";
            else if (isDisqualified) colorClass = "text-red-400";
            else if (isEvaluation) colorClass = "text-slate-400";
            else if (log.includes("APPROVED") || log.includes("COMPATIBLE")) colorClass = "text-emerald-400";
            
            return (
              <div key={idx} className={`leading-relaxed border-l-2 pl-2 border-opacity-40 ${
                isSupervisor ? 'border-cyan-500' : isDisqualified ? 'border-red-500' : 'border-slate-700'
              } ${colorClass}`}>
                <span className="text-slate-600 mr-1.5">[{new Date().toLocaleTimeString()}]</span>
                {log}
              </div>
            );
          })
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-2">
            <ShieldAlert className="w-8 h-8 text-slate-600" />
            <span>Awaiting input parameters to trigger multi-agent pipeline...</span>
          </div>
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
