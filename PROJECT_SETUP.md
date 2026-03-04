# SatyaSetu - Project Setup & Run Guide

## 🎯 Quick Start (60-70% Complete)

This project has been scaffolded with core backend and frontend components. Follow these steps to run locally.

---

## 📁 Project Structure

```
satyasetu/
├── backend/                    # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── core/              # Config, telemetry
│   │   ├── services/
│   │   │   ├── ai/            # LangGraph orchestrator ✅
│   │   │   ├── voice/         # STT/TTS stubs
│   │   │   └── ingestion/     # Document processing
│   │   └── db/                # Database clients
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                   # Next.js frontend
    ├── app/
    │   ├── page.tsx           # Landing page (scroll-story)
    │   ├── voice/             # Voice cockpit UI
    │   └── admin/             # Telemetry dashboard
    ├── components/
    └── package.json
```

---

## 🚀 Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Required for demo
OPENAI_API_KEY=your_key_here

# Optional (use mocks if not provided)
PINECONE_API_KEY=
ELEVENLABS_API_KEY=
DEEPGRAM_API_KEY=
```

### 3. Run Backend
```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- WebSocket telemetry: `ws://localhost:8000/ws/telemetry`

---

## 🎨 Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Frontend
```bash
npm run dev
```

**Frontend will be available at:** `http://localhost:3000`

---

## 📱 Pages Overview

### 1. Landing Page (`/`)
- Scroll-driven storytelling
- GSAP animations
- Spline 3D placeholder (TODO: Add actual 3D scene)
- Threat → Resolution demo flow

### 2. Voice Cockpit (`/voice`)
- Mobile-first voice interface
- Giant mic button with state animations
- Language toggle (EN/HI)
- Simulated processing flow

### 3. Admin Dashboard (`/admin`)
- Live telemetry feed
- India scam map
- Top scam types chart
- Auto-scrolling ingestion logs

---

## ✅ What's Working (60-70%)

### Backend ✅
- [x] FastAPI server structure
- [x] LangGraph orchestrator with 5 nodes:
  - safety_check
  - intent_router
  - retrieve_context
  - generate_response
  - post_process
- [x] WebSocket telemetry system
- [x] Configuration management
- [x] Voice service stubs (STT/TTS)

### Frontend ✅
- [x] Next.js + Tailwind setup
- [x] Custom design tokens (cyber-defense aesthetic)
- [x] Landing page structure
- [x] Voice UI with state management
- [x] Admin dashboard with mock data

---

## 🔧 What Needs Completion (30%)

### High Priority
1. **Streaming Voice Pipeline**
   - Integrate Whisper for real STT
   - Integrate ElevenLabs for real TTS
   - Implement streaming (STT → LLM → TTS)

2. **Database Integration**
   - Connect Pinecone vector DB
   - Set up Redis cache
   - Implement semantic caching

3. **API Endpoints**
   - Create `/api/v1/voice/query` endpoint
   - Create `/api/v1/admin/stats` endpoint
   - Wire frontend to real backend

### Medium Priority
4. **LLM Integration**
   - Replace mock responses with real OpenAI calls
   - Implement streaming token generation
   - Add confidence scoring

5. **3D Scene**
   - Create Spline "Digital Shield" scene
   - Export and integrate into landing page

### Low Priority
6. **Polish**
   - Add error boundaries
   - Implement retry logic
   - Add loading states
   - Optimize animations

---

## 🧪 Testing the Demo

### Test Backend Orchestrator
```bash
# From backend directory
python -c "
from app.services.ai.orchestrator import AIOrchestrator
import asyncio

async def test():
    orchestrator = AIOrchestrator()
    await orchestrator.initialize()
    result = await orchestrator.process_query(
        user_id='test_user',
        query='Is PM-KISAN a lottery?',
        language='en'
    )
    print(result)

asyncio.run(test())
"
```

### Test WebSocket Telemetry
Open browser console on admin dashboard and check WebSocket connection.

---

## 📚 Key Files to Review

### Backend
- `backend/app/services/ai/orchestrator.py` - **Core LangGraph logic**
- `backend/app/core/telemetry.py` - WebSocket event broadcaster
- `backend/app/core/config.py` - Environment configuration

### Frontend
- `frontend/tailwind.config.js` - Custom design tokens
- `frontend/app/page.tsx` - Landing page
- `frontend/app/voice/page.tsx` - Voice UI
- `frontend/app/admin/page.tsx` - Admin dashboard

### Documentation
- `API_CONTRACT.md` - Frontend-backend integration contract

---

## 🎯 Next Steps for Completion

1. **Choose ONE to implement first:**
   - Option A: Real voice pipeline (hardest, highest impact)
   - Option B: Vector DB + caching (medium difficulty)
   - Option C: Polish existing UI (easiest, good for demo)

2. **For hackathon demo:**
   - Focus on making the admin dashboard "feel alive"
   - Ensure landing page scroll story is smooth
   - Practice the narrative (show judges the LangGraph flow)

3. **For production:**
   - Implement all TODOs in code
   - Add authentication
   - Deploy to cloud (Railway/Vercel)

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.10+)
- Verify all dependencies installed
- Check `.env` file exists

### Frontend won't start
- Check Node version (18+)
- Run `npm install` again
- Clear `.next` cache: `rm -rf .next`

### WebSocket not connecting
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify frontend `.env.local` has correct API URL

---

## 📞 Support

For issues or questions, check:
- `MASTER_PROMPT.md` - Original build specifications
- `API_CONTRACT.md` - Integration details
- Code comments (marked with TODO)

---

**Built with:** FastAPI • LangGraph • Next.js • Tailwind • GSAP • Recharts
