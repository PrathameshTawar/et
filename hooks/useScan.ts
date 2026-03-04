"use client";

import { useState } from "react";
import { useTruthStore } from "../lib/TruthStore";

export function useScan() {
    const { startProcessing, setResult, setPipelineStep, stopProcessing } = useTruthStore();
    const [error, setError] = useState<string | null>(null);

    const performScan = async (type: string, data: any) => {
        startProcessing();
        setError(null);

        try {
            // Step 1: Extracting
            setPipelineStep(0);
            await new Promise(r => setTimeout(r, 1000));

            // Step 2: Searching
            setPipelineStep(1);
            await new Promise(r => setTimeout(r, 1500));

            // Step 3: Verifying
            setPipelineStep(2);
            await new Promise(r => setTimeout(r, 1500));

            // Step 4: Scoring
            setPipelineStep(3);
            await new Promise(r => setTimeout(r, 1000));

            // MOCK API CALL - In production, this hits /analyze/{type}
            // const response = await fetch("/api/mock-verify", {
            //     method: "POST",
            //     body: JSON.stringify({ type, data })
            // });

            // For now, return mock result
            const mockResult = {
                truth_score: 72,
                verdict: "SUSPICIOUS_CONTENT",
                explanation: "Multiple sources indicate a high probability of misinformation based on historical patterns.",
                risk_flags: ["AI_GENERATED_IMAGE", "URGENT_TONE", "UNOFFICIAL_SENDER"],
                sources: [
                    {
                        title: "Official Fact-Check Portal",
                        publisher: "GOV_IND",
                        excerpt: "This viral message has been debunked as of Jan 2024.",
                        relevance: 0.98,
                        stance: "supporting" as const
                    }
                ]
            };

            setResult(mockResult);
        } catch (err: any) {
            setError(err.message || "An unexpected error occurred during orchestration.");
            stopProcessing();
        }
    };

    return { performScan, error };
}
