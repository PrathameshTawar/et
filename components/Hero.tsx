"use client";

import React from "react";
import { motion } from "framer-motion";
import AIOrchestratorViz from "./viz/AIOrchestratorViz";

export default function Hero() {
  return (
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-deep-black pt-32 pb-20 px-6">
      {/* Background Decor */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(193,255,0,0.05)_0%,_transparent_70%)]" />

      <div className="container mx-auto max-w-7xl z-10 flex flex-col items-center text-center">
        {/* Top Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center px-4 py-1.5 rounded-full border border-neon-lime/30 bg-neon-lime/5 text-neon-lime text-[10px] font-black tracking-[0.2em] uppercase mb-8 glass-card-neon"
        >
          <span className="relative flex h-2 w-2 mr-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-lime opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-neon-lime"></span>
          </span>
          System Status: Optimal _ Active Verification
        </motion.div>

        {/* Hero Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="max-w-4xl"
        >
          <h1 className="text-6xl lg:text-8xl font-black font-space text-white leading-[1.05] tracking-tight mb-8">
            Verify <span className="text-neon-lime neon-text-glow">Truth</span> <br />
            Across Media Instantly
          </h1>

          <p className="text-lg lg:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed mb-12 font-medium">
            Deploy advanced AI orchestrators to verify information across text, audio, and video in real-time. The ultimate defense against digital misinformation.
          </p>
        </motion.div>

        {/* CTA Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex flex-wrap justify-center gap-6 mb-20"
        >
          <button className="px-10 py-4 bg-neon-lime text-black font-black uppercase tracking-widest rounded-md hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(193,255,0,0.4)] hover:shadow-[0_0_50px_rgba(193,255,0,0.6)]">
            Initialize_Engine
          </button>
          <button className="px-10 py-4 border border-white/10 text-white font-black uppercase tracking-widest rounded-md hover:bg-white/5 transition-all glass-card">
            View_Protocol
          </button>
        </motion.div>

        {/* Visual Anchor */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="w-full max-w-5xl relative"
        >
          <div className="absolute inset-0 bg-neon-lime/5 blur-[100px] rounded-full" />
          <div className="relative glass-card-neon p-4 rounded-2xl border border-neon-lime/20">
            <AIOrchestratorViz />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
