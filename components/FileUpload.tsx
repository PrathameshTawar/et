"use client";

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, 
  FileAudio, 
  FileVideo, 
  X, 
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  acceptedTypes?: string[];
  maxSizeMB?: number;
}

export function FileUpload({ 
  onFileSelect, 
  acceptedTypes = ['audio/*', 'video/*'],
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setSelectedFile(file);
    setUploadStatus('uploading');
    onFileSelect(file);
    
    // Simulate processing
    setTimeout(() => {
      setUploadStatus('success');
    }, 1000);
  };

  const removeFile = () => {
    setSelectedFile(null);
    setUploadStatus('idle');
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="w-full">
      {/* Drop Zone */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          dragActive
            ? "border-blue-500 bg-blue-500/10"
            : "border-slate-600 hover:border-slate-500 hover:bg-slate-800/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleChange}
          className="hidden"
          multiple={false}
        />

        {!selectedFile ? (
          <div className="flex flex-col items-center gap-3">
            <div className={`p-4 rounded-full ${dragActive ? 'bg-blue-500/20' : 'bg-slate-700/50'}`}>
              <Upload className={`h-8 w-8 ${dragActive ? 'text-blue-400' : 'text-slate-400'}`} />
            </div>
            <p className="text-white font-medium">
              {dragActive ? "Drop your file here" : "Click or drag to upload"}
            </p>
            <p className="text-sm text-slate-400 mt-1">
              Supports MP3, WAV, M4A Audio & MP4, WebM Video
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-between bg-slate-900/50 rounded-lg p-4 mt-4">
            {/* Filename Display */}
            <div className="flex items-center gap-3">
              {selectedFile?.type.startsWith('audio') ? (
                <FileAudio className="h-6 w-6 text-blue-400" />
              ) : ( 
                <FileVideo className="h-6 w-6 text-purple-400" />
              )}
              <div>
                <p className="text-white font-medium truncate max-w-xs">{selectedFile.name}</p> 
                <p className="text-sm text-slate-400">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>

            {/* Status Indicator */}
            {uploadStatus === 'uploading' ? (
              <span className="flex items-center gap-1 text-sm text-blue-300">
                <Loader2 className="h-5 w-5 animate-spin" /> Processing...
              </span>
            ) : uploadStatus === 'success' ? (
              <span className="flex items-center gap-1 text-sm text-green-300">
                <CheckCircle className="h-5 w-5" /> Ready
              </span>
            ) : uploadStatus === 'error' ? (
              <span className="flex items-center gap-1 text-sm text-red-300">
                <AlertCircle className="h-5 w-5" /> Error
              </span>
            ) : null}

            {/* Remove Button */}
            <button 
              onClick={(e) => {
                e.stopPropagation();
                removeFile();
              }}
              className="bg-slate-700 hover:bg-slate-600 p-2 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-slate-300" />
            </button>
          </div>
        )}
      </div>

      {/* Processing Animation */}
      {uploadStatus === 'uploading' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4"
        >
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
              <span className="text-blue-300">Processing your file...</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <motion.div 
                className="bg-blue-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 1 }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
