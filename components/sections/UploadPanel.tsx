"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileAudio, FileVideo, FileText, FileSearch, ShieldCheck, BarChart3, Loader2 } from "lucide-react";

import { useTruthStore } from "../../lib/TruthStore";
import { useScan } from "../../hooks/useScan";

type TabType = "TEXT" | "AUDIO" | "VIDEO" | "DOC";

const pipelineSteps = [
    { id: "extract", label: "Extracting Content", icon: FileText },
    { id: "search", label: "Searching Knowledge Base", icon: FileSearch },
    { id: "verify", label: "Cross-Verifying Sources", icon: ShieldCheck },
    { id: "score", label: "Calculating Truth Score", icon: BarChart3 },
];

export default function UploadPanel() {
    const [activeTab, setActiveTab] = useState<TabType>("TEXT");
    const { isProcessing, activePipelineStep, stopProcessing } = useTruthStore();
    const { performScan } = useScan();

    const startAnalysis = () => {
        performScan(activeTab, "Mock data for " + activeTab);
    };

    return (
        <section className="py-32 bg-deep-black px-6 sm:px-12 border-t border-white/5 relative">
            <div className="container mx-auto max-w-7xl">
                <div className="flex flex-col items-center text-center mb-20 space-y-4">
                    <div className="inline-flex items-center px-4 py-1 rounded bg-neon-lime/10 border border-neon-lime/20 text-neon-lime text-[10px] font-black tracking-[0.3em] uppercase mb-4">
                        Phase_01: INGESTION_PROTOCOL
                    </div>
                    <h2 className="text-5xl lg:text-6xl font-black text-white tracking-tighter uppercase italic">
                        Initiate<span className="text-neon-lime neon-text-glow ml-4">_DEEP_SCAN</span>
                    </h2>
                    <p className="text-white/30 font-mono text-[11px] max-w-2xl mx-auto uppercase tracking-[0.2em] leading-relaxed">
                        Deploy multimodal analysis engines to verify provenance and authenticity across disparate media formats.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Tab Selection */}
                    <div className="lg:col-span-3 flex flex-col gap-3">
                        {(["TEXT", "AUDIO", "VIDEO", "DOC"] as TabType[]).map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`flex items-center gap-4 px-6 py-5 rounded-lg border transition-all duration-500 font-mono ${activeTab === tab
                                    ? "bg-neon-lime text-black border-neon-lime shadow-[0_0_30px_rgba(193,255,0,0.3)] scale-[1.02]"
                                    : "bg-white/5 text-white/40 border-white/10 hover:border-neon-lime/30 hover:bg-white/[0.08]"
                                    }`}
                            >
                                {tab === "TEXT" && <FileText size={18} />}
                                {tab === "AUDIO" && <FileAudio size={18} />}
                                {tab === "VIDEO" && <FileVideo size={18} />}
                                {tab === "DOC" && <Upload size={18} />}
                                <span className="text-[10px] font-black tracking-[0.2em] uppercase">{tab}_INF_STREAM</span>
                            </button>
                        ))}
                    </div>

                    {/* Upload Area */}
                    <div className="lg:col-span-9">
                        <div className="relative group min-h-[450px] h-full rounded-xl border border-white/10 bg-deep-black flex flex-col items-center justify-center p-12 transition-all duration-700 hover:border-neon-lime/30 overflow-hidden shadow-[inset_0_0_100px_rgba(193,255,0,0.02)]">
                            {/* Decorative background grid inside panel */}
                            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[linear-gradient(rgba(193,255,0,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(193,255,0,0.2)_1px,transparent_1px)] bg-[size:20px_20px]" />

                            <AnimatePresence mode="wait">
                                {!isProcessing ? (
                                    <motion.div
                                        key="idle"
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="flex flex-col items-center text-center space-y-10 z-10"
                                    >
                                        <div className="relative group/icon">
                                            <div className="absolute -inset-4 bg-neon-lime/20 blur-xl rounded-full opacity-0 group-hover/icon:opacity-100 transition-opacity duration-700" />
                                            <div className="w-24 h-24 rounded-full bg-neon-lime/5 flex items-center justify-center text-neon-lime border border-neon-lime/20 group-hover:scale-110 transition-all duration-700 relative z-10">
                                                <Upload size={40} strokeWidth={1.5} />
                                            </div>
                                        </div>
                                        <div className="space-y-3">
                                            <h3 className="text-3xl font-black text-white tracking-tight uppercase">Mount_{activeTab}_Payload</h3>
                                            <p className="text-white/30 text-[10px] uppercase font-mono tracking-[0.3em]">
                                                ENCRYPTED_UPLOAD_SECURE_CHANNEL_READY
                                            </p>
                                        </div>
                                        <button
                                            onClick={startAnalysis}
                                            className="px-12 py-5 bg-neon-lime text-black font-black uppercase text-[10px] tracking-[0.2em] rounded hover:scale-105 transition-all duration-500 shadow-[0_0_40px_rgba(193,255,0,0.2)] hover:shadow-[0_0_60px_rgba(193,255,0,0.4)]"
                                        >
                                            Process_Media_Artifact
                                        </button>
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="processing"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="w-full max-w-3xl flex flex-col items-center space-y-16 z-10"
                                    >
                                        <div className="flex flex-col items-center gap-6">
                                            <div className="relative">
                                                <Loader2 size={48} className="text-neon-lime animate-spin opacity-50" />
                                                <div className="absolute inset-0 bg-neon-lime/10 blur-xl rounded-full animate-pulse" />
                                            </div>
                                            <span className="text-neon-lime font-mono text-[10px] font-black uppercase tracking-[0.4em] animate-pulse">Running_Verification_Sequence</span>
                                        </div>

                                        {/* Pipeline Visualizer */}
                                        <div className="w-full space-y-12">
                                            <div className="relative h-[4px] bg-white/5 rounded-full overflow-hidden">
                                                <motion.div
                                                    className="absolute top-0 left-0 h-full bg-neon-lime shadow-[0_0_15px_#C1FF00]"
                                                    animate={{ width: `${(activePipelineStep + 1) * 25}%` }}
                                                    transition={{ duration: 1.5, ease: "circOut" }}
                                                />
                                            </div>

                                            <div className="grid grid-cols-4 gap-8">
                                                {pipelineSteps.map((step, idx) => {
                                                    const Icon = step.icon;
                                                    const isActive = idx === activePipelineStep;
                                                    const isDone = idx < activePipelineStep;

                                                    return (
                                                        <div key={idx} className="flex flex-col items-center gap-4 group">
                                                            <div className={`p-4 rounded border transition-all duration-700 ${isActive ? "bg-neon-lime text-black border-neon-lime shadow-[0_0_25px_rgba(193,255,0,0.4)] scale-110" :
                                                                isDone ? "bg-neon-lime/10 text-neon-lime border-neon-lime/40" :
                                                                    "bg-white/5 text-white/10 border-white/5"
                                                                }`}>
                                                                <Icon size={24} />
                                                            </div>
                                                            <div className="flex flex-col items-center gap-1">
                                                                <span className={`text-[9px] font-mono font-black uppercase tracking-tight text-center whitespace-nowrap ${isActive ? "text-neon-lime" : "text-white/20"
                                                                    }`}>
                                                                    {step.label}
                                                                </span>
                                                                {isActive && <motion.div layoutId="pipeline-active" className="h-[2px] w-4 bg-neon-lime mt-1" />}
                                                            </div>
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        </div>

                                        <button
                                            onClick={stopProcessing}
                                            className="text-white/20 text-[9px] font-mono font-black uppercase tracking-[0.3em] border-b border-transparent hover:border-red-500/50 hover:text-red-500 transition-all duration-300"
                                        >
                                            ABORT_SEQUENCE_001
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
