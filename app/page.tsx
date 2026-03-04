"use client";

import React from "react";
import Hero from "@/components/Hero";
import UploadPanel from "@/components/sections/UploadPanel";
import ResultsView from "@/components/sections/ResultsView";
import Navbar from "@/components/Navbar";
import TelemetryHud from "@/components/common/TelemetryHud";
import PipelineLog from "@/components/common/PipelineLog";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-deep-black text-white font-inter">
      <Navbar />

      {/* Main Sections */}
      <Hero />
      <UploadPanel />
      <ResultsView />

      {/* Admin HUDs (Always present for Demo) */}
      <TelemetryHud />
      <PipelineLog />

      {/* Footer or More Sections could be added here */}
      <footer className="py-12 border-t border-white/5 text-center text-slate-600 text-sm">
        <p>&copy; 2026 SatyaSetu AI Cyber-Defense. All rights reserved.</p>
      </footer>
    </div>
  );
}

