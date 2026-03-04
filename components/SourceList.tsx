"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Shield,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';

interface Source {
  content: string;
  relevance_score: number;
  metadata?: {
    category?: string;
    language?: string;
    url?: string;
    title?: string;
  };
}

interface SourceListProps {
  sources: Source[];
  verdict?: string;
  riskLevel?: string;
}

export function SourceList({ sources, verdict, riskLevel }: SourceListProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const getVerdictIcon = () => {
    switch (verdict?.toLowerCase()) {
      case 'scam':
        return <AlertTriangle className="h-5 w-5 text-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]" />;
      case 'suspicious':
        return <Info className="h-5 w-5 text-orange-400 shadow-[0_0_10px_rgba(251,146,60,0.5)]" />;
      case 'safe':
        return <CheckCircle className="h-5 w-5 text-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />;
      default:
        return <Shield className="h-5 w-5 text-neon-lime shadow-[0_0_10px_rgba(193,255,0,0.5)]" />;
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return 'bg-green-500';
    if (score >= 0.7) return 'bg-neon-lime';
    if (score >= 0.5) return 'bg-orange-500';
    return 'bg-slate-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-deep-black/60 backdrop-blur-xl rounded-xl border border-neon-lime/10 overflow-hidden shadow-2xl"
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-6 hover:bg-neon-lime/5 transition-all duration-500"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded bg-neon-lime/5 flex items-center justify-center border border-neon-lime/20">
            <BookOpen className="h-5 w-5 text-neon-lime" />
          </div>
          <div className="text-left">
            <span className="block text-white font-black tracking-[0.2em] uppercase text-sm">INTEL_SOURCE_MANIFEST</span>
            <span className="text-[10px] text-white/30 font-mono font-black uppercase tracking-widest">NODES_IDENTIFIED: {sources.length}</span>
          </div>
          {verdict && (
            <div className="flex items-center gap-2 ml-4 px-3 py-1 rounded bg-white/5 border border-white/10 uppercase font-mono">
              {getVerdictIcon()}
              <span className="text-[9px] text-white/50 font-black tracking-widest">
                VERDICT: {verdict}
              </span>
            </div>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-neon-lime" />
        ) : (
          <ChevronDown className="h-5 w-5 text-white/20" />
        )}
      </button>

      {/* Source List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5"
          >
            <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto custom-scrollbar">
              {sources.map((source, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="group relative bg-white/[0.02] rounded-lg p-5 hover:bg-white/[0.05] transition-all border border-white/5 hover:border-neon-lime/30"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-[9px] font-mono font-black text-neon-lime/40 uppercase tracking-[0.2em]">NODE_{index + 1}</span>
                      {source.metadata?.category && (
                        <span className="text-[8px] px-2 py-0.5 rounded bg-neon-lime/10 text-neon-lime font-black uppercase tracking-wider border border-neon-lime/20">
                          {source.metadata.category}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="w-20 h-[2px] bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          className={`h-full bg-neon-lime shadow-[0_0_8px_#C1FF00]`}
                          initial={{ width: 0 }}
                          animate={{ width: `${source.relevance_score * 100}%` }}
                          transition={{ duration: 1.5 }}
                        />
                      </div>
                      <span className="text-[9px] font-mono font-black text-white/30 uppercase">
                        PROB: {(source.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-white/60 leading-relaxed font-mono italic border-l border-white/10 pl-4">
                    "{source.content}"
                  </p>

                  {source.metadata?.url && (
                    <a
                      href={source.metadata.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 mt-5 text-[9px] font-black text-neon-lime uppercase tracking-[0.2em] hover:text-white transition-colors"
                    >
                      <ExternalLink className="h-3 w-3" />
                      CROSS_REF_DATABASE
                    </a>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Loading skeleton for sources
export function SourceListSkeleton() {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-4">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-5 h-5 bg-slate-700 rounded animate-pulse" />
        <div className="w-24 h-5 bg-slate-700 rounded animate-pulse" />
      </div>
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-slate-900/50 rounded-lg p-3">
            <div className="flex justify-between mb-2">
              <div className="w-20 h-4 bg-slate-700 rounded animate-pulse" />
              <div className="w-16 h-4 bg-slate-700 rounded animate-pulse" />
            </div>
            <div className="w-full h-12 bg-slate-700 rounded animate-pulse" />
          </div>
        ))}
      </div>
    </div>
  );
}
