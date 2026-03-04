"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle, FileAudio, FileVideo } from 'lucide-react';

interface ProcessingAnimationProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  fileName?: string;
  fileType?: 'audio' | 'video';
  progress?: number;
  message?: string;
}

export function ProcessingAnimation({ 
  status, 
  fileName, 
  fileType = 'audio',
  progress = 0,
  message = "Processing your file..."
}: ProcessingAnimationProps) {
  
  if (status === 'idle') return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-md mx-auto"
    >
      <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 shadow-2xl">
        
        {/* File Icon */}
        <div className="flex justify-center mb-4">
          <motion.div
            animate={{ 
              scale: status === 'processing' ? [1, 1.1, 1] : 1,
              rotate: status === 'processing' ? [0, 5, -5, 0] : 0 
            }}
            transition={{ repeat: status === 'processing' ? Infinity : 0, duration: 2 }}
            className={`p-4 rounded-full ${
              status === 'success' ? 'bg-green-500/20' :
              status === 'error' ? 'bg-red-500/20' :
              'bg-neon-lime/20'
            }`}
          >
            {status === 'processing' ? (
              <Loader2 className={`h-10 w-10 ${fileType === 'audio' ? 'text-blue-400' : 'text-purple-400'} animate-spin`} />
            ) : status === 'success' ? (
              <CheckCircle className="h-10 w-10 text-green-400" />
            ) : status === 'error' ? (
              <AlertCircle className="h-10 w-10 text-red-400" />
            ) : fileType === 'audio' ? (
              <FileAudio className="h-10 w-10 text-blue-400" />
            ) : (
              <FileVideo className="h-10 w-10 text-purple-400" />
            )}
          </motion.div>
        </div>

        {/* Status Message */}
        <div className="text-center mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">
            {status === 'processing' && "Processing"}
            {status === 'success' && "Complete!"}
            {status === 'error' && "Error"}
          </h3>
          <p className="text-sm text-slate-400">{message}</p>
          {fileName && (
            <p className="text-xs text-slate-500 mt-1 truncate">{fileName}</p>
          )}
        </div>

        {/* Progress Bar */}
        {status === 'processing' && (
          <div className="space-y-2">
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <motion.div 
                className={`h-full rounded-full bg-neon-lime`}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500">
              <span>{progress}%</span>
              <span>Extracting {fileType === 'audio' ? 'audio' : 'frames'}...</span>
            </div>
          </div>
        )}

        {/* Processing Steps */}
        {status === 'processing' && (
          <div className="mt-4 space-y-2">
            {[
              { step: 'Uploading file', done: progress >= 20 },
              { step: 'Analyzing content', done: progress >= 40 },
              { step: 'Running AI detection', done: progress >= 70 },
              { step: 'Generating report', done: progress >= 90 },
            ].map((item, index) => (
              <motion.div 
                key={item.step}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.2 }}
                className="flex items-center gap-2 text-sm"
              >
                <div className={`w-1.5 h-1.5 rounded-full ${
                  item.done ? 'bg-green-400' : 'bg-slate-600'
                }`} />
                <span className={item.done ? 'text-slate-300' : 'text-slate-500'}>
                  {item.step}
                </span>
              </motion.div>
            ))}
          </div>
        )}

        {/* Success/Error Actions */}
        {status === 'success' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <button className="w-full py-2 px-4 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors text-sm font-medium">
              View Results
            </button>
          </motion.div>
        )}

        {status === 'error' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <button className="w-full py-2 px-4 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors text-sm font-medium">
              Try Again
            </button>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
