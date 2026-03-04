import React from "react";

export default function ThreatChart({ data }: { data: Array<{ name: string; value: number }> }) {
  return (
    <div className="rounded-lg bg-slate-900 p-4 border border-white/5">
      <h3 className="font-semibold mb-3">Top Scam Types</h3>
      <div className="space-y-2">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-3">
            <div className="w-24 text-sm text-slate-300">{d.name}</div>
            <div className="flex-1 h-3 bg-white/10 rounded" style={{ position: 'relative' }}>
              <div className="absolute left-0 top-0 h-3 bg-neon-lime rounded" style={{ width: `${Math.min(100, d.value)}%` }} />
            </div>
            <div className="w-12 text-right text-sm">{d.value}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
