import React from "react";

export default function MapPanel() {
  return (
    <div className="rounded-lg bg-slate-900 p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Live Map</h3>
      </div>
      <div className="w-full h-48 bg-black/30 rounded flex items-center justify-center">
        <div className="text-slate-400">India map placeholder with pulsing dots</div>
      </div>
    </div>
  );
}
