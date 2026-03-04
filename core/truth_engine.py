"""
Truth Engine - Core Scoring Logic
Calculates the final "Truth Score" based on multimodal evidence.
"""

from typing import List, Dict, Any, Optional
import math

class TruthScoreEngine:
    """
    Engine for calculating high-fidelity Truth Scores.
    Uses a weighted-evidence model considering:
    - Support vs Contradiction
    - Source Credibility
    - Relevance (similarity)
    - LLM Confidence
    """
    
    @staticmethod
    def calculate_score(sources: List[Dict[str, Any]], base_confidence: float = 1.0) -> Dict[str, Any]:
        """
        Calculates a 0-100 score based on evidence.
        Each source should have:
        - relevance (float 0.0-1.0)
        - stance ('supporting' | 'contradicting' | 'neutral')
        - source_credibility (float 0.0-1.0)
        """
        if not sources:
            return {
                "truth_score": 50.0, # Neutral/Uncertain
                "verdict": "UNCERTAIN",
                "supporting_count": 0,
                "contradicting_count": 0
            }
            
        total_support_weight = 0.0
        total_contradict_weight = 0.0
        
        for source in sources:
            relevance = source.get("relevance", 0.5)
            credibility = source.get("source_credibility", 0.7)
            stance = source.get("stance", "neutral")
            
            weight = relevance * credibility
            
            if stance == "supporting":
                total_support_weight += weight
            elif stance == "contradicting":
                total_contradict_weight += weight
        
        # Avoid division by zero
        total_weight = total_support_weight + total_contradict_weight
        if total_weight == 0:
            return {
                "truth_score": 50.0, 
                "verdict": "UNCERTAIN",
                "supporting_count": 0,
                "contradicting_count": 0
            }
            
        # Calculate raw ratio
        raw_score = total_support_weight / total_weight
        
        # Scale to 0-100
        final_score = raw_score * 100
        
        # Determine verdict (standardized naming)
        verdict = "LIKELY_TRUE"
        if final_score < 40:
            verdict = "THREAT_DETECTED"
        elif final_score < 65:
            verdict = "SUSPICIOUS_CONTENT"
            
        return {
            "truth_score": round(final_score, 1),
            "verdict": verdict,
            "metrics": {
                "supporting": round(total_support_weight, 2),
                "contradicting": round(total_contradict_weight, 2),
                "total_evidence": len(sources)
            }
        }
