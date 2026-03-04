"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Share2, BookOpen, Loader } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface Article {
  id: string;
  title: string;
  source: string;
  category: string;
  recommendation_score: number;
  is_exploratory: boolean;
  excerpt?: string;
  image?: string;
}

export default function NewsFeed() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [likedArticles, setLikedArticles] = useState<Set<string>>(new Set());

  const categories = ["All", "Technology", "Business", "Health", "Science"];

  // Fetch personalized feed
  useEffect(() => {
    const fetchFeed = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE}/feed?user_id=demo_user&limit=20`,
          {
            method: "GET",
            headers: { "Content-Type": "application/json" },
          }
        );

        const data = await response.json();
        if (data.status === "success") {
          setArticles(data.feed || []);
        }
      } catch (error) {
        console.error("Failed to fetch feed:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchFeed();
  }, []);

  // Track article click
  const trackArticleClick = async (articleId: string, action: string) => {
    try {
      await fetch(`${API_BASE}/feed/track-click`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_user",
          article_id: articleId,
          action,
          read_time_seconds: 120,
          scroll_depth: 0.8,
        }),
      });
    } catch (error) {
      console.error("Failed to track click:", error);
    }
  };

  const handleLike = (articleId: string) => {
    const newLiked = new Set(likedArticles);
    if (newLiked.has(articleId)) {
      newLiked.delete(articleId);
    } else {
      newLiked.add(articleId);
    }
    setLikedArticles(newLiked);
    trackArticleClick(articleId, "like");
  };

  const filteredArticles = selectedCategory
    ? articles.filter(
        (a) =>
          selectedCategory === "All" ||
          a.category.toLowerCase() === selectedCategory.toLowerCase()
      )
    : articles;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-slate-700 bg-slate-900/95 backdrop-blur">
        <div className="mx-auto max-w-3xl px-6 py-4">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="h-6 w-6 text-blue-400" />
            <h1 className="text-2xl font-bold text-white">Your News Feed</h1>
          </div>

          {/* Category Filter */}
          <div className="flex gap-3 overflow-x-auto pb-3">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() =>
                  setSelectedCategory(cat === "All" ? null : cat)
                }
                className={`whitespace-nowrap rounded-full px-4 py-2 font-medium transition ${
                  (selectedCategory === null && cat === "All") ||
                  selectedCategory === cat
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Feed */}
      <main className="mx-auto max-w-3xl px-6 py-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader className="mb-4 h-8 w-8 animate-spin text-blue-400" />
            <p className="text-slate-400">Loading your personalized feed...</p>
          </div>
        ) : (
          <AnimatePresence>
            <div className="space-y-4">
              {filteredArticles.length > 0 ? (
                filteredArticles.map((article, index) => (
                  <motion.article
                    key={article.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => trackArticleClick(article.id, "click")}
                    className="group cursor-pointer rounded-lg border border-slate-700 bg-slate-800/50 p-6 backdrop-blur transition hover:border-slate-600 hover:bg-slate-800"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        {/* Category Badge */}
                        <div className="mb-2 inline-flex items-center gap-2">
                          <span className="rounded-full bg-blue-500/20 px-3 py-1 text-xs font-medium text-blue-300">
                            {article.category}
                          </span>
                          {article.is_exploratory && (
                            <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs font-medium text-green-300">
                              New
                            </span>
                          )}
                        </div>

                        {/* Title */}
                        <h2 className="mb-2 text-lg font-semibold text-white group-hover:text-blue-400 transition">
                          {article.title}
                        </h2>

                        {/* Source & Recommendation Score */}
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                          <span>{article.source}</span>
                          <span>•</span>
                          <div className="flex items-center gap-1">
                            <span className="text-blue-400">
                              {(
                                article.recommendation_score * 100
                              ).toFixed(0)}%
                            </span>
                            <span>match</span>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-col gap-2">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLike(article.id);
                          }}
                          className={`rounded p-2 transition ${
                            likedArticles.has(article.id)
                              ? "bg-red-500/20 text-red-400"
                              : "bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-red-400"
                          }`}
                        >
                          <Heart
                            className="h-5 w-5"
                            fill={
                              likedArticles.has(article.id) ? "currentColor" : "none"
                            }
                          />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            trackArticleClick(article.id, "share");
                          }}
                          className="rounded bg-slate-700/50 p-2 text-slate-400 transition hover:bg-slate-700 hover:text-blue-400"
                        >
                          <Share2 className="h-5 w-5" />
                        </motion.button>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-slate-700">
                      <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                        initial={{ width: 0 }}
                        animate={{ width: `${article.recommendation_score * 100}%` }}
                        transition={{ duration: 0.8 }}
                      />
                    </div>
                  </motion.article>
                ))
              ) : (
                <div className="py-12 text-center">
                  <p className="text-slate-400">
                    No articles found in this category.
                  </p>
                </div>
              )}
            </div>
          </AnimatePresence>
        )}

        {/* Infinite Scroll Trigger */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="mt-12 flex flex-col items-center justify-center py-8 text-slate-400"
        >
          <Loader className="mb-2 h-5 w-5 animate-spin" />
          <p className="text-sm">Loading more articles...</p>
        </motion.div>
      </main>
    </div>
  );
}
