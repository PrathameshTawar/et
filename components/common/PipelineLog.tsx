"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Terminal } from "lucide-react";

const mockLogs = [
    "[SYS] INITIALIZING_CORE_ORCHESTRATOR...",
    "[API] INCOMING_SCAN_REQUEST: TYPE=AUDIO",
    "[AI] LOADING_WHISPER_v3_ENGINE...",
    "[S3] FETCHING_MEDIA_BLOB...",
    "[AI] TRANSCRIBING_STREAM: 0.12s",
    "[RAG] EMBEDDING_EXTRACTED_CLAIMS...",
    "[PDB] QUERYING_VECTOR_DATABASE: TOP_K=5",
    "[AI] CROSS_SOURCE_VERIFICATION_IN_PROGRESS...",
    "[ENG] CALCULATING_TRUTH_SCORE...",
    "[SYS] ANALYSIS_COMPLETE: STATUS_CODE=200"
];

export default function PipelineLog() {
    const [logs, setLogs] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let i = 0;
        const interval = setInterval(() => {
            if (i < mockLogs.length) {
                setLogs(prev => [...prev.slice(-5), mockLogs[i]]);
                i++;
            } else {
                clearInterval(interval);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="fixed bottom-6 right-6 z-[200] group">
            <div className="w-80 p-5 bg-deep-black/80 backdrop-blur-2xl border border-neon-lime/20 rounded-xl shadow-[0_0_30px_rgba(193,255,0,0.05)] space-y-4 font-mono">
                <div className="flex items-center gap-2 border-b border-neon-lime/10 pb-3">
                    <Terminal size={14} className="text-neon-lime" />
                    <span className="text-[10px] font-black text-white uppercase tracking-[0.2em]">PIPELINE_MONITOR</span>
                </div>

                <div
                    ref={scrollRef}
                    className="h-40 overflow-y-auto space-y-1.5 custom-scrollbar pr-2"
                >
                    {logs.map((log, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: 5 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="text-[9px] font-bold leading-tight whitespace-nowrap"
                        >
                            <span className="text-neon-lime mr-2">{">"}</span>
                            <span className={log.includes("[SYS]") ? "text-white" : log.includes("[AI]") ? "text-neon-lime" : "text-white/40"}>
                                {log}
                            </span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
