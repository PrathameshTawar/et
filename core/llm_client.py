"""
LLM Client for SatyaSetu
OpenAI GPT integration with streaming support
"""

import os
import json
import asyncio
from typing import Optional, AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI, OpenAI

from config import settings


class LLMClient:
    """OpenAI LLM client with streaming and safety classification"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model = "gpt-4o-mini"  # Cost-effective model
        self.fallback_model = "gpt-3.5-turbo"
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield f"[MOCK STREAM] Response for: {messages[-1]['content'][:20]}..."
            return
            
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # Fallback to gpt-3.5-turbo if gpt-4o-mini fails
            if self.model != self.fallback_model:
                self.model = self.fallback_model
                async for token in self.stream_response(messages, temperature, max_tokens):
                    yield token
            else:
                raise e
    
    async def get_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        if not self.client:
            await asyncio.sleep(0.5)
            # Basic rule-based mock for common intents
            content = messages[-1]['content'].lower()
            if "safe" in content and "verify" in content:
                return json.dumps({"safe": True, "reason": "Mock safety check passed"})
            if "intent" in content:
                return json.dumps({"intent": "scam_verification", "confidence": 0.9})
            if "verdict" in content:
                return json.dumps({
                    "verdict": "SCAM", "confidence": 0.85, "risk_level": "HIGH",
                    "explanation": "This looks like a classic lottery scam (Mock).",
                    "risk_flags": ["urgent language", "wire transfer request"],
                    "sources": ["Mock SCAM DB"]
                })
            return f"[MOCK RESPONSE] I am SatyaSetu (Mock Mode). You said: {messages[-1]['content'][:50]}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to gpt-3.5-turbo if gpt-4o-mini fails
            if self.model != self.fallback_model:
                self.model = self.fallback_model
                return await self.get_response(messages, temperature, max_tokens)
            else:
                raise e
    
    async def classify_safety(self, text: str) -> tuple[bool, str]:
        """Check if text is safe to process"""
        text_lower = text.lower()
        unsafe_keywords = [
            "hack",
            "hacking",
            "bank account",
            "steal",
            "exploit",
            "malware",
            "ransomware",
            "phishing kit",
            "ddos",
            "bypass",
        ]
        if any(keyword in text_lower for keyword in unsafe_keywords):
            return False, "Potentially harmful or illegal request detected"
        
        response = await self.get_response(
            messages=[
                {
                    "role": "system",
                    "content": """You are a safety classifier for a scam detection system. 
Respond with only valid JSON in this format:
{"safe": true/false, "reason": "brief explanation"}

Classify as unsafe if the text:
- Contains requests to help with illegal activities
- Contains harmful or dangerous content
- Contains threats or harassment"""
                },
                {
                    "role": "user",
                    "content": f"Is this safe to verify: {text}"
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        try:
            result = json.loads(response)
            return result.get("safe", True), result.get("reason", "")
        except json.JSONDecodeError:
            # If JSON parsing fails, assume safe
            return True, ""
    
    async def classify_intent(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Classify user intent"""
        
        response = await self.get_response(
            messages=[
                {
                    "role": "system",
                    "content": f"""Classify the user intent as one of: 
- 'scam_verification': User wants to verify if a message is a scam
- 'info_lookup': User is asking for information about cybersecurity
- 'general': General conversation

Respond with only valid JSON:
{{"intent": "...", "confidence": 0.0-1.0, "language": "{language}"}}"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        try:
            result = json.loads(response)
            return {
                "intent": result.get("intent", "general"),
                "confidence": result.get("confidence", 0.5),
                "language": language
            }
        except json.JSONDecodeError:
            return {"intent": "general", "confidence": 0.5, "language": language}
    
    async def generate_verdict(
        self,
        query: str,
        context: List[Dict[str, Any]],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate scam verification verdict with advanced scoring"""
        
        # 1. Analyze context for stance
        context_str = "\n".join([
            f"- SOURCE_{i}: {doc.get('content', '')[:300]}..."
            for i, doc in enumerate(context)
        ])
        
        analysis_prompt = f"""Analyze the user claim against the following sources.
Claim: {query}

Sources:
{context_str}

For each source, determine if it:
1. Supports the claim
2. Contradicts the claim
3. Is neutral/irrelevant

Respond in valid JSON:
{{
  "claim_analysis": [
    {{"source_id": "SOURCE_0", "stance": "supporting|contradicting|neutral", "reason": "..."}}
  ],
  "overall_summary": "...",
  "risk_flags": [...]
}}"""

        response = await self.get_response(
            messages=[{"role": "system", "content": "You are a factual verification analyst."},
                      {"role": "user", "content": analysis_prompt}],
            max_tokens=600,
            temperature=0.2
        )
        
        try:
            analysis = json.loads(response)
            from core.truth_engine import TruthScoreEngine
            
            # Map LLM analysis back to source data for engine
            engine_sources = []
            for item in analysis.get("claim_analysis", []):
                try:
                    sid_str = item["source_id"].split("_")[1]
                    sid = int(sid_str)
                    if sid < len(context):
                        engine_sources.append({
                            "relevance": context[sid].get("relevance_score", 0.8),
                            "stance": item["stance"],
                            "source_credibility": 0.9
                        })
                except (IndexError, ValueError):
                    continue
            
            score_data = TruthScoreEngine.calculate_score(engine_sources)
            
            return {
                "truth_score": score_data["truth_score"],
                "verdict": score_data["label"],
                "confidence": score_data["truth_score"] / 100,
                "risk_level": "HIGH" if score_data["truth_score"] < 40 else "LOW",
                "explanation": analysis.get("overall_summary", "Verification complete."),
                "risk_flags": analysis.get("risk_flags", []),
                "sources": [doc.get("content", "")[:100] for doc in context]
            }
        except Exception as e:
            return {
                "verdict": "UNCERTAIN",
                "truth_score": 50,
                "explanation": f"Error in analysis: {str(e)}",
                "risk_flags": [],
                "sources": []
            }


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
