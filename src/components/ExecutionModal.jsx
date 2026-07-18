import React, { useEffect, useState } from "react";
import { Cpu, ShieldCheck, Loader2, CheckCircle2, Zap, Activity, Clock, Globe, Info } from "lucide-react";

const EXECUTION_STEPS = [
  "Initializing AI Multi-Agent Supervisor Architecture...",
  "Ingesting Geopolitical News & Maritime Threat Feeds (Task 1)...",
  "Extracting Chokepoints, Risk Scores & Supplier Vulnerabilities...",
  "Checking Real-Time Marine AIS Tracks & Weather Conditions...",
  "Evaluating Import Port Congestion & Queue Time...",
  "Optimizing Shipping Routes via Dijkstra Graph Engine (Task 2)...",
  "Verifying Chemical Refinery Crude Grade Compatibility...",
  "Calculating Strategic Petroleum Reserve (SPR) Drawdown (Task 3)...",
  "Predicting Brent Crude Price Shock & Macro GDP Impact...",
  "Synthesizing Executive Decision Briefing & AI Rationale..."
];

export default function ExecutionModal({ isOpen, onFinished }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);
  const [secondsRemaining, setSecondsRemaining] = useState(180); // 3-minute countdown (180 seconds)

  useEffect(() => {
    if (!isOpen) {
      setCurrentStepIndex(0);
      setProgressPercent(0);
      setSecondsRemaining(180);
      return;
    }

    const totalSteps = EXECUTION_STEPS.length;
    const totalTimeMs = 12000; // 12 seconds total calculation simulation
    const stepInterval = totalTimeMs / totalSteps;

    // Countdown Timer (1-second tick)
    const countdownTimer = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    // Step Progress Timer
    const stepTimer = setInterval(() => {
      setCurrentStepIndex((prevStep) => {
        if (prevStep < totalSteps - 1) {
          const nextStep = prevStep + 1;
          setProgressPercent(Math.round(((nextStep + 1) / totalSteps) * 100));
          return nextStep;
        } else {
          clearInterval(stepTimer);
          clearInterval(countdownTimer);
          setTimeout(() => {
            onFinished();
          }, 400);
          return prevStep;
        }
      });
    }, stepInterval);

    return () => {
      clearInterval(stepTimer);
      clearInterval(countdownTimer);
    };
  }, [isOpen, onFinished]);

  if (!isOpen) return null;

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${String(mins).padStart(2, '0')}:${String(remainingSecs).padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-slate-950 bg-opacity-95 backdrop-blur-lg font-sans p-4 animate-in fade-in duration-300">
      
      {/* Prominent Center Execution Pop-Up Dialog Card */}
      <div className="max-w-xl w-full bg-[#1c2541] border-2 border-cyan-400/80 rounded-2xl p-6 shadow-[0_0_70px_rgba(6,182,212,0.5)] flex flex-col gap-5 text-slate-100 relative overflow-hidden">
        
        {/* Glow Background Gradient */}
        <div className="absolute -top-24 -right-24 w-56 h-56 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* High-Visibility Warning Banner */}
        <div className="bg-gradient-to-r from-amber-500/20 via-cyan-500/20 to-blue-500/20 border border-amber-400/50 p-3.5 rounded-xl flex items-center gap-3 shadow-lg">
          <Globe className="w-7 h-7 text-amber-400 animate-spin flex-shrink-0" />
          <div>
            <h4 className="font-bold text-xs text-amber-300 uppercase font-mono tracking-wider">
              PLEASE WAIT — MULTI-AGENT CALCULATION IN PROGRESS
            </h4>
            <p className="text-[11px] text-slate-200 mt-0.5 leading-snug font-sans">
              Fetching international threat feeds, analyzing crude logistics, and calculating SPR drawdown across supplier countries. Please wait while processing completes...
            </p>
          </div>
        </div>

        {/* Header with Countdown Clock */}
        <div className="flex items-center justify-between border-b border-slate-700/80 pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
              <Cpu className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide uppercase font-mono">
                AI MULTI-AGENT SUPERVISOR ENGINE
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                TASK 1 → TASK 2 → TASK 3 DISRUPTION INTELLIGENCE
              </p>
            </div>
          </div>
          
          {/* Prominent Live 3-Minute Countdown Display */}
          <div className="flex items-center gap-2 bg-amber-500/20 border-2 border-amber-400 text-amber-300 px-3.5 py-1.5 rounded-xl text-sm font-mono font-bold shadow-[0_0_15px_rgba(245,158,11,0.4)]">
            <Clock className="w-4 h-4 text-amber-400 animate-spin" />
            <span>EST. TIME: {formatTime(secondsRemaining)}</span>
          </div>
        </div>

        {/* Animated Progress Bar */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs font-mono text-slate-300">
            <span className="font-bold text-cyan-300">PROGRESS STATUS</span>
            <span className="text-amber-400 font-bold">{progressPercent}% COMPLETE ({currentStepIndex + 1}/{EXECUTION_STEPS.length} STEPS)</span>
          </div>
          <div className="w-full bg-slate-900 border border-slate-700 rounded-full h-3.5 overflow-hidden p-0.5 shadow-inner">
            <div 
              className="bg-gradient-to-r from-cyan-500 via-teal-400 to-amber-400 h-full rounded-full transition-all duration-300 shadow-[0_0_12px_#06b6d4]"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Step Checklist Stream */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-3.5 max-h-[220px] overflow-y-auto space-y-2 font-mono text-xs shadow-inner">
          {EXECUTION_STEPS.map((stepText, idx) => {
            const isDone = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;

            return (
              <div 
                key={idx}
                className={`flex items-center gap-3 p-2 rounded-lg transition-all duration-200 ${
                  isCurrent 
                    ? "bg-cyan-500/20 border border-cyan-400 text-cyan-200 font-bold"
                    : isDone
                    ? "text-slate-300"
                    : "text-slate-600"
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin flex-shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-700 flex-shrink-0" />
                )}
                <span className="truncate">{stepText}</span>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-slate-400 pt-1 font-mono">
          <span className="flex items-center gap-1.5 text-amber-300 font-bold">
            <Zap className="w-4 h-4 text-amber-400 animate-bounce" />
            Groq Llama-3.3-70B & MapTiler Engine Active
          </span>
          <span className="text-slate-400 font-semibold">Please wait...</span>
        </div>

      </div>
    </div>
  );
}
