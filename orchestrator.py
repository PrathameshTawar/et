"""
LangGraph-style orchestrator skeleton for SatyaSetu.
This file defines a ConversationState and the primary nodes:
  - safety_check
  - intent_router
  - retrieve_context
  - generate_response
  - post_process

Placeholders (TODO) mark where to integrate real LLM clients, vector DB, Redis, and streaming.
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConversationState:
    user_id: str
    language: str = "en"
    intent: Optional[str] = None
    query: str = ""
    audio_data: Optional[bytes] = None
    image_data: Optional[bytes] = None
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)
    verdict: Optional[str] = None
    response: Optional[str] = None
    safe: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)


async def safety_check(state: ConversationState) -> ConversationState:
    """Lightweight input guardrail."""
    from core.llm_client import get_llm_client
    llm = get_llm_client()
    safe, reason = await llm.classify_safety(state.query)
    state.safe = safe
    if not safe:
        state.response = reason
        state.meta["safety_reason"] = "harmful_content"
    return state


async def intent_router(state: ConversationState) -> ConversationState:
    """Classify user intent."""
    from core.llm_client import get_llm_client
    llm = get_llm_client()
    res = await llm.classify_intent(state.query, state.language)
    state.intent = res.get("intent", "general")
    state.meta["intent_confidence"] = res.get("confidence", 0.5)
    return state


async def retrieve_context(state: ConversationState) -> ConversationState:
    """Fetch RAG context."""
    from core.services import create_vector_db_service
    vdb = create_vector_db_service()
    state.retrieved_docs = await vdb.similarity_search(state.query)
    return state


async def generate_response(state: ConversationState) -> ConversationState:
    """Generate verdict and explanation."""
    from core.llm_client import get_llm_client
    llm = get_llm_client()
    verdict_data = await llm.generate_verdict(state.query, state.retrieved_docs, state.language)
    
    state.verdict = verdict_data.get("verdict", "UNCERTAIN")
    state.response = verdict_data.get("explanation", "Unable to verify.")
    state.meta.update({
        "confidence": verdict_data.get("confidence", 0.5),
        "risk_level": verdict_data.get("risk_level", "MEDIUM"),
        "risk_flags": verdict_data.get("risk_flags", []),
        "sources": verdict_data.get("sources", [])
    })
    return state


async def post_process(state: ConversationState) -> ConversationState:
    """Final scoring and formatting."""
    # Ensure Truth Score is formatted for frontend
    conf = state.meta.get("confidence", 0.5)
    state.meta["truth_score"] = int(conf * 100)
    
    # Cap response length for voice
    if state.response and len(state.response) > 500:
        state.response = state.response[:497] + "..."
    
    return state


async def orchestrate_multi_modal(state: ConversationState) -> ConversationState:
    """Enhanced orchestrator handling STT/OCR before logic pipeline."""
    from core.services import create_stt_service, create_vision_service
    
    # 1. Processing Multi-modal Inputs
    if state.audio_data:
        stt = create_stt_service()
        state.query = await stt.transcribe(state.audio_data, state.language)
        state.meta["original_input"] = "audio"
    
    if state.image_data:
        vision = create_vision_service()
        state.query = await vision.analyze_image(state.image_data)
        state.meta["original_input"] = "image"

    if not state.query:
        state.response = "No input detected."
        return state

    # 2. Logic Chain
    state = await safety_check(state)
    if not state.safe: return state
    state = await intent_router(state)
    state = await retrieve_context(state)
    state = await generate_response(state)
    return await post_process(state)


async def run_orchestration(user_id: str, query: str = "", audio_data: Optional[bytes] = None, 
                           image_data: Optional[bytes] = None, language: str = "en") -> ConversationState:
    """High-level entrypoint with multi-modal support."""
    state = ConversationState(user_id=user_id, language=language, query=query, 
                             audio_data=audio_data, image_data=image_data)
    return await orchestrate_multi_modal(state)


if __name__ == "__main__":
    # Quick local test
    import asyncio

    async def _test():
        s = await run_orchestration("test_user", "Is this WhatsApp message a scam about PM Kisan?")
        print(s)

    asyncio.run(_test())
