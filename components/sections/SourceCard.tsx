"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import MotionGlassCard from "../common/MotionGlassCard";
import { ExternalLink } from "lucide-react";

interface SourceCardProps {
    title: string;
    publisher: string;
    excerpt: string;
    relevance: number; // 0-1
    stance: "supporting" | "contradicting" | "neutral";
    url?: string;
}

export default function SourceCard({ title, publisher, excerpt, relevance, stance, url }: SourceCardProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <MotionGlassCard
            layout
            className="border border-neon-lime/10 hover:border-neon-lime/40 transition-all duration-500 group/card"
        >
            <div className="p-6 flex items-start gap-5">
                {/* Stance Indicator */}
                <div className={`mt-2 flex-shrink-0 w-1.5 h-1.5 rounded-full ${stance === "supporting" ? "bg-neon-lime shadow-[0_0_10px_#C1FF00]" :
                    stance === "contradicting" ? "bg-red-500 shadow-[0_0_10px_#ef4444]" :
                        "bg-white/20"
                    }`} />

                <div className="flex-grow space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-[9px] font-mono font-black text-white/30 uppercase tracking-[0.3em]">
                            SOURCE_ID: {publisher}
                        </span>
                        <div className="flex items-center gap-3">
                            <div className="w-16 h-[2px] bg-white/5 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-neon-lime"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${relevance * 100}%` }}
                                    transition={{ duration: 1.5 }}
                                />
                            </div>
                            <span className="text-[10px] font-mono font-black text-neon-lime">{Math.round(relevance * 100)}%</span>
                        </div>
                    </div>

                    <h4 className="text-sm font-bold text-white leading-relaxed group-hover/card:text-neon-lime transition-colors">{title}</h4>

                    <div className="flex items-center gap-4">
                        <span className={`px-2 py-0.5 rounded border text-[8px] font-black uppercase tracking-[0.2em] transition-all duration-300 ${stance === "supporting" ? "bg-neon-lime/10 border-neon-lime/20 text-neon-lime shadow-[0_0_10px_rgba(193,255,0,0.1)]" :
                            stance === "contradicting" ? "bg-red-500/10 border-red-500/20 text-red-500" :
                                "bg-white/5 border-white/10 text-white/40"
                            }`}>
                            {stance}
                        </span>
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="text-[10px] font-mono font-black text-white/20 hover:text-white transition-all flex items-center gap-2 uppercase tracking-widest"
                        >
                            {isExpanded ? "COLLAPSE_LOG" : "EXPAND_INTEL"}
                        </button>
                    </div>
                </div>

                {url && (
                    <a href={url} target="_blank" rel="noopener noreferrer" className="p-2.5 bg-white/5 rounded border border-white/5 text-white/30 hover:text-neon-lime hover:border-neon-lime/30 transition-all shadow-xl">
                        <ExternalLink size={14} />
                    </a>
                )}
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-6 pb-6 border-t border-white/5 pt-5 bg-white/[0.02]"
                    >
                        <p className="text-[11px] text-white/50 leading-relaxed font-medium font-mono leading-relaxed border-l-2 border-neon-lime/20 pl-4 py-1 italic">
                            "{excerpt}"
                        </p>
                    </motion.div>
                )}
            </AnimatePresence>
        </MotionGlassCard>
    );
}
