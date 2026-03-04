"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

interface Source {
    title: string;
    publisher: string;
    excerpt: string;
    relevance: number;
    stance: "supporting" | "contradicting" | "neutral";
    url?: string;
}

interface ScanResult {
    truth_score: number;
    verdict: string;
    explanation: string;
    risk_flags: string[];
    sources: Source[];
}

interface TruthStoreContextType {
    result: ScanResult | null;
    isProcessing: boolean;
    activePipelineStep: number;
    setResult: (result: ScanResult) => void;
    startProcessing: () => void;
    stopProcessing: () => void;
    setPipelineStep: (step: number) => void;
}

const TruthStoreContext = createContext<TruthStoreContextType | undefined>(undefined);

export function TruthStoreProvider({ children }: { children: ReactNode }) {
    const [result, setResultState] = useState<ScanResult | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [activePipelineStep, setActivePipelineStep] = useState(0);

    const setResult = (res: ScanResult) => {
        setResultState(res);
        setIsProcessing(false);
    };

    const startProcessing = () => {
        setIsProcessing(true);
        setResultState(null);
        setActivePipelineStep(0);
    };

    const stopProcessing = () => {
        setIsProcessing(false);
    };

    const setPipelineStep = (step: number) => {
        setActivePipelineStep(step);
    };

    return (
        <TruthStoreContext.Provider value={{
            result,
            isProcessing,
            activePipelineStep,
            setResult,
            startProcessing,
            stopProcessing,
            setPipelineStep
        }}>
            {children}
        </TruthStoreContext.Provider>
    );
}

export function useTruthStore() {
    const context = useContext(TruthStoreContext);
    if (context === undefined) {
        throw new Error("useTruthStore must be used within a TruthStoreProvider");
    }
    return context;
}
