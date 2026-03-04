"use client";

import React from "react";
import { motion } from "framer-motion";
import TruthScoreMeter from "./TruthScoreMeter";
import SourceCard from "./SourceCard";

import { useTruthStore } from "../../lib/TruthStore";

export default function ResultsView() {
    const { result } = useTruthStore();

    if (!result) return null;

    return (
        <section className="py-32 bg-deep-black px-6 sm:px-12 relative overflow-hidden">
            {/* Background Accent */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-neon-lime/5 blur-[150px] -z-10" />

            <div className="container mx-auto max-w-7xl">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
                    {/* Main Score Column */}
                    <div className="lg:col-span-4 space-y-12">
                        <div className="space-y-2">
                            <h3 className="text-2xl font-black text-white uppercase tracking-[0.3em] font-mono">
                                ANALYSIS<span className="text-neon-lime">_</span>RESULT
                            </h3>
                            <div className="h-[2px] w-20 bg-neon-lime" />
                        </div>

                        <div className="relative group">
                            <div className="absolute -inset-4 bg-neon-lime/5 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                            <TruthScoreMeter score={result.truth_score} />
                        </div>

                        <div className="p-8 bg-deep-black border border-neon-lime/20 rounded-xl space-y-6 shadow-[0_0_30px_rgba(193,255,0,0.02)] glass-card">
                            <h4 className="text-[10px] font-black uppercase text-neon-lime tracking-[0.3em] border-b border-neon-lime/10 pb-3">NEURAL_REASONING</h4>
                            <ul className="space-y-4">
                                {result.risk_flags.map((flag, i) => (
                                    <li key={i} className="flex gap-4 text-xs text-white/60 leading-relaxed group">
                                        <span className="text-neon-lime font-mono font-black group-hover:animate-pulse">0{i + 1}</span>
                                        <span className="group-hover:text-white transition-colors">{flag}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Sources Column */}
                    <div className="lg:col-span-8 space-y-12">
                        <div className="flex items-end justify-between border-b border-white/5 pb-4">
                            <div className="space-y-2">
                                <h3 className="text-2xl font-black text-white uppercase tracking-[0.3em] font-mono">
                                    VERIFICATION<span className="text-neon-lime">_</span>CEDENTIALS
                                </h3>
                                <p className="text-[10px] font-mono text-white/30 uppercase tracking-[0.2em]">CROSS_SOURCE_AUTHENTICATION_LOG</p>
                            </div>
                            <span className="px-4 py-2 bg-neon-lime/5 border border-neon-lime/20 rounded text-[10px] font-black font-mono text-neon-lime tracking-[0.2em]">
                                {result.sources.length}_NODES_VALIDATED
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-h-[800px] overflow-y-auto pr-4 custom-scrollbar">
                            {result.sources.map((source, i) => (
                                <SourceCard key={i} {...source} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
