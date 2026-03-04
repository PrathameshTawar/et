"use client";

import React from "react";
import MapPanel from "../../components/MapPanel";
import ThreatChart from "../../components/ThreatChart";
import IngestionLog from "../../components/IngestionLog";
import useMockTelemetry from "../../hooks/useMockTelemetry";

export default function AdminDashboard() {
  const { logs, chartData } = useMockTelemetry();

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <header className="px-4 py-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="font-semibold">SatyaSetu — Mission Control</div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <MapPanel />
          <ThreatChart data={chartData} />
        </div>

        <div className="md:col-span-1">
          <IngestionLog logs={logs} />
        </div>
      </main>
    </div>
  );
}
