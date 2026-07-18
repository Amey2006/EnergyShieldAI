import React, { useState, useEffect } from "react";
import { ChevronRight, ChevronLeft, X, Sparkles, CheckCircle2, MousePointerClick } from "lucide-react";

const TOUR_STEPS = [
  {
    target: "disruption-simulator",
    title: "1. Select Disruption Scenario",
    content: "Select a disruption scenario to begin the simulation (e.g., Hormuz Blockage, Red Sea Strike, or Arabian Sea Cyclone).",
    requiresAction: true,
    actionPrompt: "Action Hint: Click any disruption scenario checkbox or click Next."
  },
  {
    target: "execute-workflow-btn",
    title: "2. Execute Optimization",
    content: "Great! Now click EXECUTE MULTI-AGENT WORKFLOW to start the AI analysis.",
    requiresAction: true,
    actionPrompt: "Action Hint: Click the Execute button to begin multi-agent analysis."
  },
  {
    target: "digital-twin-canvas",
    title: "3. MapTiler Digital Twin & SPR Canvas",
    content: "Explore real-time cartographic layers powered by MapTiler showing supplier ports, refineries, SPR sites (Mangalore, Padur, Visakhapatnam), tankers, and threat blockages.",
    requiresAction: false,
    actionPrompt: ""
  },
  {
    target: "orchestration-console",
    title: "4. Multi-Agent Orchestration Console",
    content: "Watch live multi-agent execution & timer stream directly inside the console as Task 1, Task 2, and Task 3 process data.",
    requiresAction: false,
    actionPrompt: ""
  },
  {
    target: "executive-briefing",
    title: "5. Executive Decision Briefing",
    content: "Synthesizes final AI Architect reasoning explaining WHY specific suppliers, ports, routes, and SPR release amounts were selected.",
    requiresAction: false,
    actionPrompt: ""
  }
];

export default function GuidedTour({ isOpen, onClose, onComplete, onActionTriggered }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [highlightStyle, setHighlightStyle] = useState({});
  const [stepCompleted, setStepCompleted] = useState(false);

  const step = TOUR_STEPS[currentStepIndex];

  useEffect(() => {
    if (!isOpen) return;

    setStepCompleted(false);

    const targetElem = document.getElementById(step.target);
    if (targetElem) {
      targetElem.scrollIntoView({ behavior: "smooth", block: "center" });
      const rect = targetElem.getBoundingClientRect();
      setHighlightStyle({
        top: `${rect.top + window.scrollY - 6}px`,
        left: `${rect.left + window.scrollX - 6}px`,
        width: `${rect.width + 12}px`,
        height: `${rect.height + 12}px`,
      });

      const handleTargetClick = () => {
        setStepCompleted(true);
        if (onActionTriggered) onActionTriggered(step.target);
      };

      targetElem.addEventListener("click", handleTargetClick);
      const windowClickListener = () => setStepCompleted(true);
      window.addEventListener("click", windowClickListener);

      return () => {
        targetElem.removeEventListener("click", handleTargetClick);
        window.removeEventListener("click", windowClickListener);
      };
    }
  }, [isOpen, currentStepIndex, step]);

  if (!isOpen) return null;

  const isFirst = currentStepIndex === 0;
  const isLast = currentStepIndex === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      onComplete();
    } else {
      setCurrentStepIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirst) setCurrentStepIndex((prev) => prev - 1);
  };

  return (
    <div className="fixed inset-0 z-[9990] overflow-hidden pointer-events-none">
      
      {/* COMPLETELY TRANSPARENT BACKDROP (NO BLUR, NO DIMMING, 100% VISIBLE) */}
      <div className="absolute inset-0 bg-transparent pointer-events-none" />

      {/* Pulsing Spotlight Ring around Current Target Component */}
      <div
        className={`absolute border-2 rounded-xl shadow-[0_0_35px_rgba(6,182,212,0.9)] transition-all duration-300 pointer-events-none ${
          step.requiresAction && !stepCompleted
            ? "border-amber-400 animate-pulse shadow-[0_0_40px_rgba(245,158,11,0.9)]"
            : "border-cyan-400 animate-pulse"
        }`}
        style={highlightStyle}
      />

      {/* Walkthrough Card */}
      <div 
        className="fixed bottom-6 right-6 md:right-12 max-w-md w-full bg-[#1c2541]/95 border-2 border-cyan-500/80 text-slate-100 p-5 rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.9)] backdrop-blur-md z-[10000] flex flex-col gap-4 font-sans pointer-events-auto animate-in fade-in slide-in-from-bottom-5 duration-300"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-700/80 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400 animate-spin" />
            <span className="font-bold text-xs text-cyan-300 font-mono uppercase tracking-wider">
              INTERACTIVE GUIDED TOUR ({currentStepIndex + 1}/{TOUR_STEPS.length})
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div>
          <h4 className="font-bold text-sm text-white mb-1.5 flex items-center gap-2">
            {step.title}
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed font-sans mb-2">
            {step.content}
          </p>

          {/* Action Prompt Banner */}
          {step.requiresAction && (
            <div className={`mt-2 p-2.5 rounded-lg border text-xs font-mono font-bold flex items-center gap-2 transition-all ${
              stepCompleted 
                ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400"
                : "bg-amber-500/10 border-amber-500/40 text-amber-300 animate-pulse"
            }`}>
              {stepCompleted ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Action Verified! Click Next to proceed.</span>
                </>
              ) : (
                <>
                  <MousePointerClick className="w-4 h-4 text-amber-400 flex-shrink-0 animate-bounce" />
                  <span>{step.actionPrompt}</span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Navigation Controls */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-700/80 font-mono text-xs">
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 underline"
          >
            Skip Tutorial
          </button>

          <div className="flex items-center gap-2">
            {!isFirst && (
              <button
                onClick={handlePrev}
                className="flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg font-semibold transition"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
            )}

            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg font-bold transition shadow-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 shadow-[0_0_15px_rgba(6,182,212,0.4)]"
            >
              {isLast ? (
                <>
                  Finish Tutorial
                  <CheckCircle2 className="w-4 h-4" />
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
