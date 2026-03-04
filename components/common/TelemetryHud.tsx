"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Cpu, Zap, Lock, Database } from "lucide-react";

export default function TelemetryHud() {
    const [isVisible, setIsVisible] = useState(true);
    const [stats, setStats] = useState({
        latency: 242,
        tokens: 1240,
        cost: 0.042,
        nodes: 8,
        wafBlocks: 0
    });

    useEffect(() => {
        const interval = setInterval(() => {
            setStats(prev => ({
                ...prev,
                latency: 200 + Math.floor(Math.random() * 100),
                wafBlocks: prev.wafBlocks + (Math.random() > 0.95 ? 1 : 0)
            }));
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-6 left-6 z-[200]">
            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ opacity: 0, x: -20, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="p-5 bg-deep-black/80 backdrop-blur-2xl border border-neon-lime/20 rounded-xl shadow-[0_0_30px_rgba(193,255,0,0.05)] w-72 space-y-5 overflow-hidden font-mono"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between border-b border-neon-lime/10 pb-3">
                            <div className="flex items-center gap-2">
                                <Activity size={14} className="text-neon-lime animate-pulse" />
                                <span className="text-[10px] font-black text-white uppercase tracking-[0.2em]">SYSTEM_TELEMETRY</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[8px] text-neon-lime font-bold animate-pulse">LIVE</span>
                                <div className="w-2 h-2 rounded-full bg-neon-lime shadow-[0_0_10px_#C1FF00]" />
                            </div>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <span className="text-[9px] text-white/30 uppercase tracking-tighter">API_Latency</span>
                                <div className="text-sm font-black text-white">{stats.latency}ms</div>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[9px] text-white/30 uppercase tracking-tighter">Token_Usage</span>
                                <div className="text-sm font-black text-white">{stats.tokens}</div>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[9px] text-white/30 uppercase tracking-tighter">Infra_Cost</span>
                                <div className="text-sm font-black text-neon-lime">${stats.cost.toFixed(3)}</div>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[9px] text-white/30 uppercase tracking-tighter">Active_Nodes</span>
                                <div className="text-sm font-black text-white">{stats.nodes}</div>
                            </div>
                        </div>

                        {/* WAF Logic */}
                        <div className="flex items-center justify-between px-3 py-2 bg-neon-lime/5 rounded border border-neon-lime/10">
                            <div className="flex items-center gap-2">
                                <Lock size={12} className="text-neon-lime/50" />
                                <span className="text-[9px] font-bold text-white/50 uppercase tracking-widest">WAF_Protocol</span>
                            </div>
                            <span className="text-[9px] font-black text-neon-lime neon-text-glow">PROTECTED</span>
                        </div>

                        <div className="flex justify-between items-center text-[7px] text-white/20 uppercase tracking-[0.3em]">
                            <span>SECURE_ENCLAVE</span>
                            <span>TX_042_99</span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <button
                onClick={() => setIsVisible(!isVisible)}
                className="mt-4 w-12 h-12 bg-deep-black border border-neon-lime/20 rounded-lg flex items-center justify-center text-white/50 hover:text-neon-lime transition-all duration-300 shadow-[0_0_20px_rgba(0,0,0,0.5)] group"
            >
                <Zap size={18} className={`${isVisible ? "text-neon-lime" : ""} group-hover:drop-shadow-[0_0_8px_rgba(193,255,0,0.6)]`} />
            </button>
        </div>
    );
}
