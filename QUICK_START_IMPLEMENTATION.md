# SatyaSetu - Quick Start Implementation Guide

## ⚡ Get Up & Running in 24 Hours

This guide shows you exactly what to do RIGHT NOW to get a working MVP.

---

## STEP 1: Setup Environment (30 minutes)

### 1.1 Install Dependencies

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

# Add new dependencies
pip install langchain langchain-openai python-dotenv aiofiles

# Frontend
cd ../frontend
npm install
```

### 1.2 Setup API Keys

Create `backend/.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Google Cloud (optional, use mock for now)
GOOGLE_CLOUD_API_KEY=...

# Database
DATABASE_URL=sqlite:///./test.db

# Settings
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_PER_MINUTE=60
```

---

## STEP 2: Implement LLM Client (1 hour)

Create file: `backend/core/llm_client.py`

```python
import asyncio
import os
from typing import Optional, AsyncGenerator
from openai import AsyncOpenAI, OpenAI

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # or "gpt-4" for better quality
    
    async def stream_response(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response token by token"""
        
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
    
    async def get_response(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Get complete LLM response"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def classify_safety(self, text: str) -> tuple[bool, str]:
        """Check if text is safe to process"""
        
        response = await self.get_response(
            messages=[
                {
                    "role": "system",
                    "content": "You are a safety classifier. Respond with only JSON: {\"safe\": true/false, \"reason\": \"string\"}"
                },
                {
                    "role": "user",
                    "content": f"Is this safe to verify: {text}"
                }
            ],
            max_tokens=50
        )
        
        import json
        result = json.loads(response)
        return result["safe"], result.get("reason", "")
```

---

## STEP 3: Create Vector DB with Sample Data (1 hour)

Create file: `backend/services/vector_db_service.py`

```python
import os
import json
from typing import List, Dict
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from pathlib import Path

class VectorDBService:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )
    
    async def load_scams_data(self):
        """Load initial scam detection data"""
        
        scams = [
            # Hindi Scams
            {
                "text": "आपके बैंक अकाउंट में समस्या है। यह लिंक खोलें: bit.ly/update",
                "language": "hi",
                "type": "phishing",
                "risk_level": "high",
                "source": "RBI_Alert"
            },
            {
                "text": "आप 10 लाख रुपये की सरकारी योजना के लिए योग्य हैं। अभी क्लिक करें",
                "language": "hi",
                "type": "government_scheme_scam",
                "risk_level": "high",
                "source": "PIB"
            },
            # English Scams
            {
                "text": "Your account has been compromised. Click here to verify: link.com",
                "language": "en",
                "type": "phishing",
                "risk_level": "high",
                "source": "RBI_Alert"
            },
            {
                "text": "You've won Rs 50 lakh! Claim your prize now",
                "language": "en",
                "type": "lottery_scam",
                "risk_level": "high",
                "source": "Complaint_Database"
            },
            # Legitimate Messages
            {
                "text": "राजस्थान सरकार सभी किसानों को 6000 रुपये प्रति साल देगी।",
                "language": "hi",
                "type": "legitimate",
                "risk_level": "low",
                "source": "PIB_Official"
            },
            {
                "text": "RBI has issued new UPI guidelines for payment security.",
                "language": "en",
                "type": "legitimate",
                "risk_level": "low",
                "source": "RBI_Official"
            }
        ]
        
        # Add to vector store with metadata
        for scam in scams:
            self.vectorstore.add_texts(
                texts=[scam["text"]],
                metadatas=[{
                    "language": scam["language"],
                    "type": scam["type"],
                    "risk_level": scam["risk_level"],
                    "source": scam["source"]
                }]
            )
        
        print(f"✅ Loaded {len(scams)} scam samples into vector DB")
    
    async def retrieve_context(
        self,
        query: str,
        k: int = 3,
        language: str = "en"
    ) -> List[Dict]:
        """Retrieve similar scams and guidelines"""
        
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter={"language": language}  # Optional language filter
        )
        
        context = []
        for doc, score in results:
            context.append({
                "text": doc.page_content,
                "similarity": score,
                "metadata": doc.metadata
            })
        
        return context
```

---

## STEP 4: Update Orchestrator (1.5 hours)

Replace `backend/orchestrator.py` with:

```python
"""
Updated SatyaSetu Orchestrator with real LLM and vector DB
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json

from core.llm_client import LLMClient
from services.vector_db_service import VectorDBService


@dataclass
class ConversationState:
    user_id: str
    language: str = "en"
    query: str = ""
    intent: Optional[str] = None
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)
    response: Optional[str] = None
    verdict: Optional[str] = None  # SCAM, SAFE, UNCERTAIN
    confidence: float = 0.0
    risk_level: Optional[str] = None  # LOW, MEDIUM, HIGH
    sources: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    safe: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_db = VectorDBService()
    
    async def initialize(self):
        """Initialize services"""
        await self.vector_db.load_scams_data()
        print("✅ Orchestrator initialized")
    
    async def safety_check(self, state: ConversationState) -> ConversationState:
        """Check if input is safe to process using LLM"""
        
        safe, reason = await self.llm.classify_safety(state.query)
        state.safe = safe
        
        if not safe:
            state.response = "Cannot process this request. Please provide a message to verify instead."
            state.meta["safety_reason"] = reason
        
        return state
    
    async def intent_router(self, state: ConversationState) -> ConversationState:
        """Classify intent of user query"""
        
        response = await self.llm.get_response(
            messages=[
                {
                    "role": "system",
                    "content": "Classify the intent as one of: 'scam_verification', 'info_lookup', 'general'. Respond only with JSON: {\"intent\": \"...\"}"
                },
                {
                    "role": "user",
                    "content": state.query
                }
            ],
            max_tokens=50
        )
        
        try:
            result = json.loads(response)
            state.intent = result.get("intent", "general")
        except:
            state.intent = "general"
        
        return state
    
    async def retrieve_context(self, state: ConversationState, timeout: float = 3.0) -> ConversationState:
        """Retrieve relevant scam patterns and guidelines from vector DB"""
        
        try:
            # Get similar scams/patterns from vector DB
            state.retrieved_docs = await self.vector_db.retrieve_context(
                query=state.query,
                k=3,
                language=state.language
            )
        except Exception as e:
            print(f"⚠️ Vector DB error: {e}")
            state.retrieved_docs = []
        
        return state
    
    async def generate_response(self, state: ConversationState) -> ConversationState:
        """Generate verification verdict using LLM"""
        
        if not state.safe:
            return state
        
        # Build context from retrieved docs
        context = "\n".join([
            f"- {doc['text']} (Similarity: {doc['similarity']:.2f})"
            for doc in state.retrieved_docs
        ])
        
        # Create verification prompt
        prompt = f"""You are a expert in detecting scams and misinformation targeting Indian citizens.
        
User query: {state.query}

Similar patterns found:
{context if context else "No similar patterns found"}

Analyze this message and provide:
1. Verdict: Is this a SCAM, SAFE, or UNCERTAIN?
2. Confidence: 0.0-1.0
3. Risk Level: LOW, MEDIUM, or HIGH
4. Explanation: Why (in {state.language} if possible)
5. Risk Flags: What indicators of scam (if any)
6. Sources: Which sources support your verdict

Respond ONLY with valid JSON:
{{
    "verdict": "SCAM|SAFE|UNCERTAIN",
    "confidence": 0.x,
    "risk_level": "LOW|MEDIUM|HIGH",
    "explanation": "...",
    "risk_flags": ["flag1", "flag2"],
    "sources": ["source1", "source2"]
}}"""
        
        response = await self.llm.get_response(
            messages=[
                {"role": "system", "content": "You are a scam detection expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        try:
            result = json.loads(response)
            state.verdict = result.get("verdict")
            state.confidence = result.get("confidence", 0.0)
            state.risk_level = result.get("risk_level")
            state.response = result.get("explanation")
            state.risk_flags = result.get("risk_flags", [])
            state.sources = result.get("sources", [])
        except json.JSONDecodeError:
            state.response = response
            state.verdict = "UNCERTAIN"
            state.confidence = 0.5
        
        return state
    
    async def post_process(self, state: ConversationState) -> ConversationState:
        """Final processing and formatting"""
        
        # Ensure all fields are populated
        if not state.verdict:
            state.verdict = "UNCERTAIN"
        if state.confidence == 0:
            state.confidence = 0.5
        if not state.response:
            state.response = "Unable to verify this message"
        
        return state
    
    async def process(self, query: str, user_id: str = "user123", language: str = "en") -> ConversationState:
        """Main entry point - run full pipeline"""
        
        state = ConversationState(
            user_id=user_id,
            language=language,
            query=query
        )
        
        # Run pipeline
        state = await self.safety_check(state)
        if not state.safe:
            return state
        
        state = await self.intent_router(state)
        state = await self.retrieve_context(state)
        state = await self.generate_response(state)
        state = await self.post_process(state)
        
        return state
```

---

## STEP 5: Update API Route (45 minutes)

Update `backend/api/routes/voice.py`:

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
from orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

class VoiceQueryRequest(BaseModel):
    query: str
    language: str = "en"
    user_id: str = "user123"

class VoiceQueryResponse(BaseModel):
    verdict: str
    confidence: float
    risk_level: str
    explanation: str
    risk_flags: list
    sources: list

@router.post("/query", response_model=VoiceQueryResponse)
async def query_voice(request: VoiceQueryRequest):
    """Process voice/text query and return verification verdict"""
    
    try:
        # Initialize orchestrator
        await orchestrator.initialize()
        
        # Process query through pipeline
        state = await orchestrator.process(
            query=request.query,
            user_id=request.user_id,
            language=request.language
        )
        
        return VoiceQueryResponse(
            verdict=state.verdict,
            confidence=state.confidence,
            risk_level=state.risk_level,
            explanation=state.response,
            risk_flags=state.risk_flags,
            sources=state.sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_pipeline():
    """Quick test endpoint"""
    
    test_queries = [
        "Your bank account is compromised. Update now: bit.ly/update",
        "You've won Rs 50 lakh! Claim your prize",
        "RBI has issued new UPI security guidelines"
    ]
    
    results = []
    for query in test_queries:
        state = await orchestrator.process(query)
        results.append({
            "query": query,
            "verdict": state.verdict,
            "confidence": state.confidence
        })
    
    return {"test_results": results}
```

---

## STEP 6: Test Immediately (15 minutes)

### Start Backend:

```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Test in PowerShell:

```powershell
# Test safety check
curl -X POST http://localhost:8000/api/voice/query -H "Content-Type: application/json" -d '{
  "query": "Your bank account is compromised. Update now: bit.ly/update",
  "language": "en"
}'

# Should return:
# {
#   "verdict": "SCAM",
#   "confidence": 0.95,
#   "risk_level": "HIGH",
#   ...
# }

# Test with legitimate message
curl -X POST http://localhost:8000/api/voice/query -H "Content-Type: application/json" -d '{
  "query": "What is the PM Kisan Yojana scheme?",
  "language": "en"
}'

# Test endpoint
curl http://localhost:8000/api/voice/test
```

---

## STEP 7: Frontend Update (45 minutes)

Update `frontend/pages/voice.tsx`:

```typescript
import { useState } from 'react';
import axios from 'axios';

interface VerificationResult {
  verdict: string;
  confidence: number;
  risk_level: string;
  explanation: string;
  risk_flags: string[];
  sources: string[];
}

export default function VoicePage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('en');

  const handleSubmit = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/voice/query',
        {
          query,
          language,
          user_id: 'user123'
        }
      );
      
      setResult(response.data);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to verify');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">SatyaSetu Verification</h1>
      
      {/* Language Selector */}
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="mb-4 p-2 border rounded"
      >
        <option value="en">English</option>
        <option value="hi">हिंदी (Hindi)</option>
      </select>
      
      {/* Query Input */}
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Paste the message you want to verify..."
        className="w-full p-4 border rounded mb-4 h-24"
      />
      
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-500 text-white px-6 py-2 rounded"
      >
        {loading ? 'Verifying...' : 'Verify'}
      </button>
      
      {/* Results */}
      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="text-xl font-bold mb-2">
            Verdict: 
            <span className={`ml-2 ${result.verdict === 'SCAM' ? 'text-red-500' : 'text-green-500'}`}>
              {result.verdict}
            </span>
          </h2>
          
          <p className="mb-2">
            Confidence: <span className="font-bold">{(result.confidence * 100).toFixed(1)}%</span>
          </p>
          
          <p className="mb-2">
            Risk Level: <span className="font-bold">{result.risk_level}</span>
          </p>
          
          <p className="mb-2">Explanation: {result.explanation}</p>
          
          {result.risk_flags.length > 0 && (
            <div className="mb-2">
              <p className="font-bold">Risk Flags:</p>
              <ul className="list-disc ml-4">
                {result.risk_flags.map((flag, i) => (
                  <li key={i}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
          
          {result.sources.length > 0 && (
            <div>
              <p className="font-bold">Sources:</p>
              <ul className="list-disc ml-4">
                {result.sources.map((source, i) => (
                  <li key={i}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 🎉 YOU'RE DONE!

Now you have:
- ✅ LLM integration working
- ✅ Vector DB with sample scams
- ✅ API endpoint returning verdicts
- ✅ Frontend displaying results

**Total time: ~4-6 hours**

This is your **minimum viable product**. Now you can:
1. Add more test cases
2. Integrate real STT/TTS
3. Add more languages
4. Optimize response time
5. Deploy to production

---

## Next: Add STT/TTS (Optional, for voice)

If you want voice input:

```bash
pip install openai google-cloud-speech google-cloud-texttospeech
```

Then implement the audio handlers in `services/voice/stt.py` and `services/voice/tts.py` using the same patterns above.

**You're ready to ship! 🚀**
