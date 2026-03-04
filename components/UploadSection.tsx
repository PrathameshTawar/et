"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileAudio, FileText, CheckCircle2, Loader2 } from "lucide-react";

export default function UploadSection() {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [complete, setComplete] = useState(false);

    const handleSimulateUpload = () => {
        setIsUploading(true);
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            setUploadProgress(progress);
            if (progress >= 100) {
                clearInterval(interval);
                setComplete(true);
                setIsUploading(false);
            }
        }, 100);
    };

    return (
        <section className="py-24 bg-deep-black px-6 sm:px-12">
            <div className="container mx-auto max-w-4xl">
                <div className="text-center mb-12">
                    <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Multi-Modal Threat Analysis</h2>
                    <p className="text-slate-400">Upload audio, video, or documents for deep-scan AI verification.</p>
                </div>

                <div className="relative group p-1 rounded-2xl bg-gradient-to-br from-neon-lime/20 to-transparent scanlines">
                    <div className="glass-card-neon bg-deep-black/60 backdrop-blur-xl border border-neon-lime/20 rounded-2xl p-12 flex flex-col items-center justify-center min-h-[400px]">
                        <AnimatePresence mode="wait">
                            {!isUploading && !complete ? (
                                <motion.div
                                    key="idle"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="flex flex-col items-center text-center space-y-6"
                                >
                                    <div className="w-20 h-20 rounded-full bg-neon-lime/10 flex items-center justify-center text-neon-lime border border-neon-lime/20 group-hover:scale-110 transition-transform duration-500">
                                        <Upload size={32} />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white">Drag and Drop Files</h3>
                                        <p className="text-slate-500 text-sm mt-1">Supports MP3, WAV, JPG, PNG, PDF (Max 20MB)</p>
                                    </div>
                                    <button
                                        onClick={handleSimulateUpload}
                                        className="px-6 py-3 bg-neon-lime text-deep-black font-bold rounded-lg hover:shadow-[0_0_15px_rgba(193,255,0,0.3)] transition-all"
                                    >
                                        Select Files
                                    </button>
                                    <div className="flex gap-8 pt-8">
                                        <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-widest font-bold">
                                            <FileAudio size={14} className="text-neon-lime" /> Audio Scan
                                        </div>
                                        <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-widest font-bold">
                                            <FileText size={14} className="text-neon-lime" /> OCR Analysis
                                        </div>
                                    </div>
                                </motion.div>
                            ) : isUploading ? (
                                <motion.div
                                    key="uploading"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex flex-col items-center space-y-6 w-full max-w-md"
                                >
                                    <Loader2 size={48} className="text-neon-lime animate-spin" />
                                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                                        <motion.div
                                            className="h-full bg-neon-lime shadow-[0_0_10px_rgba(193,255,0,0.6)]"
                                            initial={{ width: 0 }}
                                            animate={{ width: `${uploadProgress}%` }}
                                        />
                                    </div>
                                    <p className="text-neon-lime font-mono text-sm tracking-tighter">PROCESS_STATUS: UPLOADING_ENCRYPTED_PACKET_{uploadProgress}%</p>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="complete"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="flex flex-col items-center space-y-4"
                                >
                                    <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 border border-green-500/20">
                                        <CheckCircle2 size={40} />
                                    </div>
                                    <h3 className="text-2xl font-bold text-white">Upload Secure</h3>
                                    <p className="text-slate-400">Analyzing payload for potential threats...</p>
                                    <button
                                        onClick={() => setComplete(false)}
                                        className="text-neon-lime text-sm underline pt-4"
                                    >
                                        Upload Another
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </section>
    );
}
