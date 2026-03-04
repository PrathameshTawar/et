"use client";

import React, { useEffect, useState } from "react";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";

interface TruthScoreMeterProps {
    score: number; // 0-100
}

export default function TruthScoreMeter({ score }: TruthScoreMeterProps) {
    const count = useMotionValue(0);
    const rounded = useTransform(count, (latest) => Math.round(latest));

    useEffect(() => {
        const controls = animate(count, score, { duration: 2, ease: "easeOut" });
        return controls.stop;
    }, [score]);

    const getColor = (s: number) => {
        if (s >= 75) return "#22c55e"; // Green
        if (s >= 40) return "#fb923c"; // Orange
        return "#ef4444"; // Red
    };

    const strokeColor = getColor(score);

    return (
        <div className="flex flex-col items-center justify-center p-10 bg-deep-black/40 rounded-2xl border border-neon-lime/20 backdrop-blur-xl shadow-[0_0_50px_rgba(193,255,0,0.02)] relative overflow-hidden group">
            {/* Background Glow */}
            <div
                className="absolute inset-0 opacity-5 blur-[100px] transition-colors duration-1000 bg-neon-lime"
            />

            <div className="relative w-56 h-56">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <defs>
                        <filter id="meterGlow">
                            <feGaussianBlur stdDeviation="3" result="blur" />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>

                    {/* Background Circle */}
                    <circle
                        cx="50"
                        cy="50"
                        r="42"
                        fill="transparent"
                        stroke="#C1FF00"
                        strokeOpacity="0.05"
                        strokeWidth="4"
                    />

                    {/* Progress Circle */}
                    <motion.circle
                        cx="50"
                        cy="50"
                        r="42"
                        fill="transparent"
                        stroke="#C1FF00"
                        strokeWidth="4"
                        strokeLinecap="butt"
                        strokeDasharray="264"
                        filter="url(#meterGlow)"
                        initial={{ strokeDashoffset: 264 }}
                        animate={{ strokeDashoffset: 264 - (264 * score) / 100 }}
                        transition={{ duration: 2.5, ease: "circOut" }}
                    />
                </svg>

                {/* Center Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="flex items-baseline">
                        <motion.span className="text-6xl font-black text-white tracking-tighter neon-text-glow">
                            <motion.span>{rounded}</motion.span>
                        </motion.span>
                        <span className="text-neon-lime font-mono text-sm ml-1">%</span>
                    </div>
                    <span className="text-[9px] font-mono text-white/40 uppercase tracking-[0.4em] mt-2 font-black">VERITY_QUOTIENT</span>
                </div>
            </div>

            <div className="mt-10 text-center space-y-4">
                <div
                    className="inline-flex px-5 py-2 rounded border border-neon-lime/30 bg-neon-lime/5 text-neon-lime text-[10px] font-black uppercase tracking-[0.2em] transition-all duration-500 shadow-[0_0_15px_rgba(193,255,0,0.1)]"
                >
                    {score >= 75 ? "NODE_SECURE" : score >= 40 ? "ANOMALY_DETECTED" : "THREAT_CONFIRMED"}
                </div>
                <div className="flex flex-col gap-1 items-center">
                    <p className="text-[8px] text-white/30 font-mono uppercase tracking-widest">
                        Confidence_Interval: {(score > 80 ? "0.998" : score > 50 ? "0.842" : "0.412")}
                    </p>
                    <div className="h-1 w-32 bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                            className="h-full bg-neon-lime"
                            initial={{ width: 0 }}
                            animate={{ width: `${score}%` }}
                            transition={{ duration: 2 }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
