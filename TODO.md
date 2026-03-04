# SatyaSetu Implementation TODO

## Phase 1: Backend Core (Week 1)

### Day 1: Setup & LLM Client ✅ DONE
- [x] Read and understand all 7 documentation files
- [x] Create `backend/core/llm_client.py` - OpenAI client with streaming
- [x] Add langchain dependencies to requirements.txt

### Day 2: Vector Database & Scam Data ✅ DONE
- [x] Create `backend/services/vector_db_service.py` - Chroma DB with sample scams
- [x] Add sample scam dataset (20+ examples in Hindi/English)

### Day 3: Update Core Orchestrator ✅ IN PROGRESS
- [x] Integrate LLM client (imports added to orchestrator.py)
- [x] Integrate vector DB (imports added)
- [x] Add confidence scoring - in llm_client.py
- [x] Add risk level classification - in llm_client.py

### Day 4: Connect API Endpoint
- [ ] Add `/api/voice/query` endpoint to voice.py
- [ ] Connect to orchestrator
- [ ] Add request/response models

### Day 5: Testing & Documentation
- [ ] Test with curl/Postman
- [ ] Create test cases

## Phase 2: Frontend & Voice I/O (Week 2)
- [ ] Voice Recorder Component
- [ ] Results Display Component
- [ ] Language Support
- [ ] Admin Dashboard

## Phase 3: Validation & Deployment (Week 3)
- [ ] Comprehensive Testing
- [ ] Load Testing
- [ ] Docker & Deployment
- [ ] Final Polish

---

## Files Created/Modified:

1. **et/et/backend/requirements.txt** - Added langchain, chromadb dependencies
2. **et/et/backend/core/llm_client.py** - NEW: OpenAI LLM client with streaming
3. **et/et/backend/services/vector_db_service.py** - NEW: Chroma DB with scam data
4. **et/et/TODO.md** - This tracking file
