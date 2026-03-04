"use client";

import React from "react";
import MotionGlassCard from "./common/MotionGlassCard";

export default function ThreatCard() {
  return (
    <MotionGlassCard className="p-6 border-neon-lime/10 hover:border-neon-lime/30">
      <div className="mb-3 text-sm text-slate-400">Incoming message</div>
      <div className="rounded-lg bg-black/40 p-4 border border-white/5">
        <p className="text-white font-medium">You won a lottery! Click the link to claim your prize.</p>
        <div className="mt-3 text-xs text-red-400">Threat Detected</div>
      </div>
      <div className="mt-4 text-sm text-slate-300">Scroll to see how SatyaSetu analyzes and verifies this message.</div>
    </MotionGlassCard>
  );
}
