"use client";

import React from "react";
import { motion } from "framer-motion";

const nodes = [
    { id: "input", x: 100, y: 250, label: "DATA_STRM", color: "#C1FF00" },
    { id: "whisper", x: 280, y: 120, label: "AUDIO_INF", color: "#C1FF00" },
    { id: "vision", x: 280, y: 380, label: "VISUAL_INF", color: "#C1FF00" },
    { id: "orchestrator", x: 480, y: 250, label: "CORE_ORCH", color: "#FFFFFF" },
    { id: "rag", x: 680, y: 120, label: "VDB_RETR", color: "#C1FF00" },
    { id: "verifier", x: 680, y: 380, label: "FACT_CHECK", color: "#C1FF00" },
    { id: "output", x: 860, y: 250, label: "TRUTH_SCORE", color: "#C1FF00" },
];

const connections = [
    { from: "input", to: "whisper" },
    { from: "input", to: "vision" },
    { from: "whisper", to: "orchestrator" },
    { from: "vision", to: "orchestrator" },
    { from: "orchestrator", to: "rag" },
    { from: "orchestrator", to: "verifier" },
    { from: "rag", to: "output" },
    { from: "verifier", to: "output" },
    // Complex cross-connections
    { from: "rag", to: "verifier", dashed: true },
    { from: "whisper", to: "vision", dashed: true },
];

export default function AIOrchestratorViz() {
    return (
        <div className="relative w-full h-[550px] bg-black/40 rounded-2xl border border-neon-lime/20 backdrop-blur-md overflow-hidden group shadow-[inset_0_0_50px_rgba(193,255,0,0.02)] scanlines corner-brackets">
            {/* SVG Background Grid */}
            <div className="absolute inset-0 opacity-20 pointer-events-none">
                <svg width="100%" height="100%">
                    <defs>
                        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#C1FF00" strokeWidth="0.5" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
            </div>

            <svg className="w-full h-full" viewBox="0 0 960 500">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#C1FF00" stopOpacity="0" />
                        <stop offset="50%" stopColor="#C1FF00" stopOpacity="0.5" />
                        <stop offset="100%" stopColor="#C1FF00" stopOpacity="0" />
                    </linearGradient>
                </defs>

                {/* Connection Lines */}
                {connections.map((conn, i) => {
                    const fromNode = nodes.find((n) => n.id === conn.from)!;
                    const toNode = nodes.find((n) => n.id === conn.to)!;

                    return (
                        <g key={`conn-${i}`}>
                            <motion.line
                                x1={fromNode.x}
                                y1={fromNode.y}
                                x2={toNode.x}
                                y2={toNode.y}
                                stroke="#C1FF00"
                                strokeOpacity={conn.dashed ? "0.1" : "0.2"}
                                strokeWidth={conn.dashed ? "1" : "1.5"}
                                strokeDasharray={conn.dashed ? "5,5" : "none"}
                                initial={{ pathLength: 0, opacity: 0 }}
                                animate={{ pathLength: 1, opacity: 1 }}
                                transition={{ duration: 1.5, delay: i * 0.1 }}
                            />
                            {!conn.dashed && (
                                <motion.circle
                                    r="2.5"
                                    fill="#C1FF00"
                                    filter="url(#glow)"
                                    animate={{
                                        cx: [fromNode.x, toNode.x],
                                        cy: [fromNode.y, toNode.y],
                                        opacity: [0, 1, 0]
                                    }}
                                    transition={{
                                        duration: 2.5,
                                        repeat: Infinity,
                                        delay: i * 0.5,
                                        ease: "linear"
                                    }}
                                />
                            )}
                        </g>
                    );
                })}

                {/* Nodes */}
                {nodes.map((node) => (
                    <g key={node.id}>
                        {/* Node Outer Glow */}
                        <motion.circle
                            cx={node.x}
                            cy={node.y}
                            r="12"
                            fill="transparent"
                            stroke={node.color}
                            strokeWidth="1"
                            strokeOpacity="0.3"
                            animate={{ scale: [1, 1.8], opacity: [0.6, 0] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                        {/* Node Core */}
                        <motion.circle
                            cx={node.x}
                            cy={node.y}
                            r="6"
                            fill={node.color}
                            filter="url(#glow)"
                            whileHover={{ scale: 1.5 }}
                            className="cursor-pointer"
                        />
                        {/* Label */}
                        <motion.text
                            x={node.x}
                            y={node.y + 30}
                            textAnchor="middle"
                            className="fill-white/70 text-[9px] font-mono tracking-[0.2em] font-black"
                        >
                            {node.label}
                        </motion.text>
                    </g>
                ))}
            </svg>

            {/* Decorative Overlays */}
            <div className="absolute top-6 left-8 flex items-center gap-4">
                <div className="flex flex-col">
                    <span className="text-[10px] font-mono text-neon-lime font-black uppercase tracking-[0.2em] mb-1">
                        Deployment_Phase: 04_Verification
                    </span>
                    <div className="h-[2px] w-32 bg-white/10 overflow-hidden">
                        <motion.div
                            className="h-full bg-neon-lime"
                            animate={{ x: [-128, 128] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        />
                    </div>
                </div>
            </div>

            <div className="absolute bottom-6 left-8 text-[9px] font-mono text-white/30 tracking-[0.1em] uppercase">
                Packet_Loss: 0.0003% | Latency: 12ms
            </div>
        </div>
    );
}
