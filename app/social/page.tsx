"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Zap,
  BarChart3,
  Calendar,
  Image,
  Wand2,
} from "lucide-react";

// API Client
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface BrandProfile {
  id: string;
  name: string;
  keywords: string[];
  tone: string;
  audience_persona: Record<string, unknown>;
  platforms: string[];
}

interface GeneratedContent {
  topic: string;
  platforms: Record<
    string,
    {
      caption: string;
      hashtags: string[];
      status: string;
    }
  >;
}

export default function SocialDashboard() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "generate" | "schedule" | "analytics">(
    "dashboard"
  );
  const [brand, setBrand] = useState<BrandProfile | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState("");

  // Generate content
  const handleGenerateContent = async () => {
    if (!topic || !brand) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/social/generate-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_id: brand.id,
          topic,
          platforms: brand.platforms,
          campaign_goal: "engagement",
        }),
      });

      const data = await response.json();
      if (data.status === "success") {
        setGeneratedContent(data.content_package);
      }
    } catch (error) {
      console.error("Generation failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-600 p-2">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">
                AI Social Media Engine
              </h1>
            </div>
            <div className="text-sm text-slate-400">Brand: {brand?.name}</div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-700 bg-slate-800/50">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex gap-8">
            {[
              { key: "dashboard", label: "Dashboard", icon: BarChart3 },
              { key: "generate", label: "Generate", icon: Wand2 },
              { key: "schedule", label: "Schedule", icon: Calendar },
              { key: "analytics", label: "Analytics", icon: BarChart3 },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as typeof activeTab)}
                className={`flex items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition ${
                  activeTab === key
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-slate-400 hover:text-slate-300"
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        {activeTab === "generate" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Content Generation Form */}
            <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
              <h2 className="mb-6 text-xl font-bold text-white">
                Generate Content
              </h2>

              <div className="space-y-4">
                {/* Topic Input */}
                <div>
                  <label className="block text-sm font-medium text-slate-300">
                    Content Topic
                  </label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., 'New product launch announcement'"
                    className="mt-2 w-full rounded-lg border border-slate-600 bg-slate-900 px-4 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>

                {/* Generate Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleGenerateContent}
                  disabled={loading || !topic}
                  className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition disabled:opacity-50 hover:bg-blue-700"
                >
                  {loading ? "Generating..." : "Generate Content"}
                </motion.button>
              </div>
            </div>

            {/* Generated Content Preview */}
            {generatedContent && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white">Generated Content</h3>

                {Object.entries(generatedContent.platforms).map(
                  ([platform, content]) => (
                    <motion.div
                      key={platform}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="rounded-lg border border-slate-700 bg-slate-800 p-6"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-blue-400 capitalize">
                          {platform}
                        </h4>
                        <span className="rounded bg-green-500/20 px-3 py-1 text-xs font-medium text-green-400">
                          {content.status}
                        </span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <label className="text-sm font-medium text-slate-400">
                            Caption
                          </label>
                          <p className="mt-1 text-slate-300">{content.caption}</p>
                        </div>

                        <div>
                          <label className="text-sm font-medium text-slate-400">
                            Hashtags
                          </label>
                          <div className="mt-1 flex flex-wrap gap-2">
                            {content.hashtags.map((tag, i) => (
                              <span
                                key={i}
                                className="rounded bg-blue-500/20 px-2 py-1 text-xs text-blue-300"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>

                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          className="mt-4 flex items-center gap-2 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Schedule Post <ArrowRight className="h-4 w-4" />
                        </motion.button>
                      </div>
                    </motion.div>
                  )
                )}
              </div>
            )}
          </motion.div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid gap-6"
          >
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: "Total Posts", value: "24", icon: Zap },
                { label: "Avg Engagement", value: "4.5%", icon: BarChart3 },
                { label: "Total Reach", value: "45K", icon: Image },
                { label: "Best Platform", value: "Instagram", icon: Calendar },
              ].map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className="rounded-lg border border-slate-700 bg-slate-800 p-6"
                >
                  <Icon className="mb-2 h-5 w-5 text-blue-400" />
                  <p className="text-sm text-slate-400">{label}</p>
                  <p className="mt-1 text-2xl font-bold text-white">{value}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
