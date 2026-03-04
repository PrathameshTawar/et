"use client";

import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  Play,
  Scissors,
  FileText,
  Image as ImageIcon,
  Download,
  Loader2,
  Check,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface VideoData {
  video_id: string;
  filename: string;
  duration: number;
  scenes: Scene[];
  captions: Caption[];
  thumbnails: Thumbnail[];
}

interface Scene {
  id: string;
  start_time: number;
  end_time: number;
  type: string;
  importance: number;
}

interface Caption {
  id: string;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
}

interface Thumbnail {
  variant_id: string;
  style: string;
  ctr_potential: number;
  has_text: boolean;
}

type Step = "upload" | "analyze" | "edit" | "export";

export default function VideoEditor() {
  const [activeStep, setActiveStep] = useState<Step>("upload");
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([
    "instagram",
  ]);

  const steps: { id: Step; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "upload", label: "Upload Video", icon: Upload },
    { id: "analyze", label: "Analyze", icon: Play },
    { id: "edit", label: "Edit", icon: Scissors },
    { id: "export", label: "Export", icon: Download },
  ];

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/videos/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json().catch(() => ({}));
      if (data && data.status === "success" && data.video) {
        setVideoData({
          video_id: String(data.video.video_id ?? ""),
          filename: String(data.video.filename ?? ""),
          duration: 0,
          scenes: Array.isArray(data.video.scenes) ? data.video.scenes : [],
          captions: Array.isArray(data.video.captions) ? data.video.captions : [],
          thumbnails: Array.isArray(data.video.thumbnails) ? data.video.thumbnails : [],
        });
        setActiveStep("analyze");
      } else {
        throw new Error(data.message || "Upload failed: Invalid response");
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred during upload");
    } finally {
      setLoading(false);
    }
  };

  // Analyze video
  const handleAnalyzeVideo = async () => {
    if (!videoData) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/videos/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoData.video_id,
          analyze_scenes: true,
          generate_captions: true,
          generate_thumbnails: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json().catch(() => ({}));
      if (data && data.status === "success" && data.analysis) {
        const analysis = data.analysis ?? {};
        setVideoData((prev) =>
          prev
            ? {
                ...prev,
                scenes: Array.isArray(analysis.scenes) ? analysis.scenes : [],
                captions: Array.isArray(analysis.captions) ? analysis.captions : [],
                thumbnails: Array.isArray(analysis.thumbnails) ? analysis.thumbnails : [],
                duration: Number(analysis.duration ?? 0),
              }
            : null
        );
        setActiveStep("edit");
      } else {
        throw new Error(data.message || "Analysis failed: Invalid response");
      }
    } catch (error) {
      console.error("Analysis failed:", error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred during analysis");
    } finally {
      setLoading(false);
    }
  };

  // Export video
  const handleExportVideo = async () => {
    if (!videoData) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/videos/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoData.video_id,
          platforms: selectedPlatforms,
          include_captions: true,
          auto_select_thumbnail: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      const data = await response.json().catch(() => ({}));
      if (data && (data.status === "processing" || data.status === "success")) {
        setActiveStep("export");
      } else {
        throw new Error(data.message || "Export failed: Invalid response");
      }
    } catch (error) {
      console.error("Export failed:", error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred during export");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <h1 className="text-3xl font-bold text-white">AI Video Editor</h1>
          <p className="mt-1 text-slate-400">
            Turn raw footage into platform-ready videos
          </p>
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="border-b border-red-700 bg-red-900/50">
          <div className="mx-auto max-w-7xl px-6 py-4">
            <div className="rounded-lg bg-red-800/50 p-4 text-red-200">
              <p className="font-medium">Error: {error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Steps Progress */}
      <div className="border-b border-slate-700 bg-slate-800/50">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = activeStep === step.id;
              const isCompleted =
                steps.findIndex((s) => s.id === activeStep) >
                steps.findIndex((s) => s.id === step.id);

              return (
                <React.Fragment key={step.id}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    onClick={() => isCompleted && setActiveStep(step.id)}
                    className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg p-3 transition ${
                      isActive
                        ? "bg-blue-500/20 text-blue-400"
                        : isCompleted
                          ? "bg-green-500/20 text-green-400"
                          : "text-slate-400"
                    }`}
                  >
                    <div
                      className={`rounded-full p-2 ${
                        isActive
                          ? "bg-blue-500/30"
                          : isCompleted
                            ? "bg-green-500/30"
                            : "bg-slate-700/30"
                      }`}
                    >
                      {isCompleted ? (
                        <Check className="h-5 w-5" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </div>
                    <span className="text-xs font-medium">{step.label}</span>
                  </motion.div>

                  {index < steps.length - 1 && (
                    <div
                      className={`flex-1 h-1 mx-2 transition ${
                        isCompleted ? "bg-green-500" : "bg-slate-700"
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* STEP 1: Upload */}
        {activeStep === "upload" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-dashed border-slate-600 bg-slate-800/50 p-12 text-center"
          >
            <Upload className="mx-auto mb-4 h-12 w-12 text-blue-400" />
            <h2 className="mb-2 text-2xl font-bold text-white">
              Upload Your Video
            </h2>
            <p className="mb-6 text-slate-400">
              Supported formats: MP4, WebM, AVI (Max 2GB)
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              className="hidden"
            />

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => fileInputRef.current?.click()}
              className="mx-auto flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3 font-semibold text-white hover:bg-blue-700"
            >
              <Upload className="h-5 w-5" />
              Choose Video
            </motion.button>
          </motion.div>
        )}

        {/* STEP 2: Analyze */}
        {activeStep === "analyze" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
              <h2 className="mb-4 text-xl font-bold text-white">
                Video Analysis
              </h2>
              <p className="mb-6 text-slate-400">
                AI is analyzing your video for scenes, audio, and optimal
                thumbnails...
              </p>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleAnalyzeVideo}
                disabled={loading}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    Analyze Video
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* STEP 3: Edit */}
        {activeStep === "edit" && videoData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Scenes */}
            <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
              <div className="mb-4 flex items-center gap-2">
                <Scissors className="h-5 w-5 text-blue-400" />
                <h3 className="text-lg font-bold text-white">Detected Scenes</h3>
              </div>

              <div className="space-y-3">
                {videoData.scenes.map((scene: Scene) => (
                  <motion.div
                  key={scene.id}
                  whileHover={{ x: 4 }}
                  className="flex items-center gap-4 rounded bg-slate-900 p-4"
                  >
                  <div className="flex-1">
                    <p className="font-medium text-white capitalize">
                    {scene.type}
                    </p>
                    <p className="text-sm text-slate-400">
                    {Number(scene.start_time ?? 0).toFixed(1)}s -{" "}
                    {Number(scene.end_time ?? 0).toFixed(1)}s
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-blue-400">
                    {Number((scene.importance ?? 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-slate-400">Importance</div>
                  </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Captions */}
            {videoData.captions.length > 0 && (
              <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
                <div className="mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-400" />
                  <h3 className="text-lg font-bold text-white">
                    Generated Captions
                  </h3>
                </div>

                <div className="space-y-3">
                  {videoData.captions.slice(0, 3).map((caption) => (
                    <div
                      key={caption.id}
                      className="rounded bg-slate-900 p-4"
                    >
                      <p className="text-sm text-slate-400">
                        {Number(caption.start_time ?? 0).toFixed(1)}s -{" "}
                        {Number(caption.end_time ?? 0).toFixed(1)}s
                      </p>
                      <p className="mt-1 text-white">{caption.text}</p>
                      <div className="mt-2 text-xs text-slate-500">
                        Confidence: {Number((caption.confidence ?? 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Thumbnails */}
            {videoData.thumbnails.length > 0 && (
              <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
                <div className="mb-4 flex items-center gap-2">
                  <ImageIcon className="h-5 w-5 text-blue-400" />
                  <h3 className="text-lg font-bold text-white">
                    Thumbnail Options
                  </h3>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {videoData.thumbnails.map((thumb) => (
                    <motion.div
                      key={thumb.variant_id}
                      whileHover={{ scale: 1.05 }}
                      className="cursor-pointer rounded-lg border border-slate-600 bg-slate-900 p-4 transition hover:border-blue-400"
                    >
                      <div className="aspect-video rounded bg-gradient-to-br from-blue-500 to-blue-600 mb-3" />
                      <p className="font-medium text-white capitalize">
                        {thumb.style}
                      </p>
                      <p className="text-sm text-blue-400">
                        {Number((thumb.ctr_potential ?? 0) * 100).toFixed(0)}% CTR
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Proceed to Export */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveStep("export")}
              className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700"
            >
              Proceed to Export
            </motion.button>
          </motion.div>
        )}

        {/* STEP 4: Export */}
        {activeStep === "export" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-slate-700 bg-slate-800 p-6"
          >
            <h2 className="mb-6 text-xl font-bold text-white">
              Export for Platforms
            </h2>

            {/* Platform Selection */}
            <div className="mb-6 grid grid-cols-2 gap-4">
              {[
                { id: "instagram", label: "Instagram Reels" },
                { id: "youtube", label: "YouTube Shorts" },
                { id: "tiktok", label: "TikTok" },
                { id: "linkedin", label: "LinkedIn" },
              ].map((platform) => (
                <motion.button
                  key={platform.id}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => {
                    const updated = selectedPlatforms.includes(platform.id)
                      ? selectedPlatforms.filter((p) => p !== platform.id)
                      : [...selectedPlatforms, platform.id];
                    setSelectedPlatforms(updated);
                  }}
                  className={`rounded-lg border-2 px-4 py-3 font-medium transition ${
                    selectedPlatforms.includes(platform.id)
                      ? "border-blue-500 bg-blue-500/20 text-blue-400"
                      : "border-slate-600 bg-slate-900 text-slate-400 hover:border-slate-500"
                  }`}
                >
                  {platform.label}
                </motion.button>
              ))}
            </div>

            {/* Export Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleExportVideo}
              disabled={loading || selectedPlatforms.length === 0}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-green-600 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="h-5 w-5" />
                  Export to {selectedPlatforms.length} Platform
                  {selectedPlatforms.length !== 1 ? "s" : ""}
                </>
              )}
            </motion.button>
          </motion.div>
        )}
      </main>
    </div>
  );
}