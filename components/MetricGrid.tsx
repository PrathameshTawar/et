"use client";

import React from "react";
import MotionGlassCard from "./common/MotionGlassCard";

interface Stat {
  value: string;
  label: string;
  highlight?: boolean;
}

const stats: Stat[] = [
  { value: "49B", label: "Events/sec" },
  { value: "1.2B*", label: "We sandbox attachments per day", highlight: true },
  { value: "28M", label: "Threats blocked" },
  { value: "2B", label: "Packets monitored" },
];

export default function MetricGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 scanlines">
      {stats.map((s, idx) => (
        <MotionGlassCard
          key={idx}
          className={`p-6 text-center relative corner-brackets ${
            s.highlight ? "bg-neon-lime text-black" : "bg-deep-black/50 text-white"
          }`}
        >
          <div
            className={`text-4xl font-extrabold tracking-tight ${
              s.highlight ? "text-black" : "text-white"
            }`}
          >
            {s.value}
          </div>
          <div className="text-sm mt-2 text-white/60">{s.label}</div>
        </MotionGlassCard>
      ))}
    </div>
  );
}
