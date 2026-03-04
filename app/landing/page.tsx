"use client";

import React from "react";
import Hero from "../../components/Hero";
import ThreatCard from "../../components/ThreatCard";
import SplineContainer from "../../components/SplineContainer";
import MetricGrid from "../../components/MetricGrid";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-deep-black text-white">
      <header className="sticky top-0 z-20 backdrop-blur bg-black/40 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-xl font-semibold">SatyaSetu</div>
          <button className="rounded-md px-4 py-2 border border-neon-lime text-neon-lime hover:bg-neon-lime/10 transition-colors">Launch App</button>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-12">
        <Hero />
        {/* metric grid with stats, highlight one card to mimic R2 video */}
        <div className="mt-16">
          <MetricGrid />
        </div>

        <section>
          <h2 className="text-2xl font-bold font-space text-neon-lime mb-4">The Threat</h2>
          <div className="md:flex md:gap-6">
            <div className="flex-1">
              <ThreatCard />
            </div>
            <div className="hidden md:block md:w-1/3">
              <SplineContainer />
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold font-space text-neon-lime mb-4">Resolution</h2>
          <p className="text-slate-300">Verified by SatyaSetu AI Engine. (Pipeline schematic placeholder)</p>
        </section>
      </main>
    </div>
  );
}
