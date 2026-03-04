"""
LangGraph AI Orchestrator for SatyaSetu
Stateful multi-step AI workflow with safety guardrails
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """State object shared across all graph nodes"""
    user_id: str
    language: str  # "en" or "hi"
    query: str
    intent: str  # scam_verify | scheme_lookup | general_question | offline_fallback
    retrieved_docs: list
    response: str
    safe: bool
    confidence: float
    risk_flags: list[str]
    sources: list[str]
    messages: Annotated[Sequence[BaseMessage], "conversation history"]
    timestamp: str


class AIOrchestrator:
    """
    LangGraph-based AI orchestrator with explicit workflow nodes.
    Handles: Safety → Intent → Retrieval → Generation → Post-processing
    """
    
    def __init__(self, telemetry_manager=None):
        self.telemetry = telemetry_manager
        self.llm = None
        self.graph = None
        
    async def initialize(self):
        """Initialize LLM and build the graph"""
        logger.info("🧠 Initializing AI Orchestrator...")
        
        # TODO: Load from environment
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            streaming=True
        )
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
        logger.info("✅ AI Orchestrator initialized")
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("safety_check", self.safety_check_node)
        workflow.add_node("intent_router", self.intent_router_node)
        workflow.add_node("retrieve_context", self.retrieve_context_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("post_process", self.post_process_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("safety_check")
        
        # Safety check → Intent router (or END if unsafe)
        workflow.add_conditional_edges(
            "safety_check",
            self._route_after_safety,
            {
                "safe": "intent_router",
                "unsafe": END
            }
        )
        
        # Intent router → Retrieve context (or offline fallback)
        workflow.add_conditional_edges(
            "intent_router",
            self._route_after_intent,
            {
                "online": "retrieve_context",
                "offline": "generate_response"  # Skip retrieval for offline
            }
        )
        
        # Retrieve → Generate
        workflow.add_edge("retrieve_context", "generate_response")
        
        # Generate → Post-process
        workflow.add_edge("generate_response", "post_process")
        
        # Post-process → END
        workflow.add_edge("post_process", END)
        
        return workflow.compile()
    
    # ==================== GRAPH NODES ====================
    
    async def safety_check_node(self, state: ConversationState) -> ConversationState:
        """
        Node 1: Safety Check
        Detect prompt injection, jailbreak attempts, unsafe requests
        """
        logger.info(f"🛡️ Safety Check: {state['query'][:50]}...")
        
        if self.telemetry:
            await self.telemetry.emit("safety_check_start", {
                "user_id": state["user_id"],
                "query_preview": state["query"][:100]
            })
        
        # Simple safety checks (TODO: Use nvidia-guardrails or similar)
        unsafe_patterns = [
            "ignore previous instructions",
            "jailbreak",
            "pretend you are",
            "financial advice",
            "legal advice"
        ]
        
        query_lower = state["query"].lower()
        risk_flags = []
        
        for pattern in unsafe_patterns:
            if pattern in query_lower:
                risk_flags.append(f"unsafe_pattern:{pattern}")
        
        is_safe = len(risk_flags) == 0
        
        state["safe"] = is_safe
        state["risk_flags"] = risk_flags
        
        if not is_safe:
            state["response"] = "I cannot process this request. Please ask about government schemes or scam verification."
            if self.telemetry:
                await self.telemetry.emit("safety_block", {
                    "user_id": state["user_id"],
                    "reason": risk_flags
                })
        
        return state
    
    async def intent_router_node(self, state: ConversationState) -> ConversationState:
        """
        Node 2: Intent Classification
        Route to: scam_verify | scheme_lookup | general_question | offline_fallback
        """
        logger.info("🧭 Intent Routing...")
        
        query = state["query"].lower()
        
        # Simple keyword-based intent detection (TODO: Use LLM classifier)
        if any(word in query for word in ["scam", "fake", "fraud", "verify", "trust"]):
            intent = "scam_verify"
        elif any(word in query for word in ["scheme", "yojana", "benefit", "subsidy", "pm kisan"]):
            intent = "scheme_lookup"
        elif "offline" in query or state.get("offline_mode"):
            intent = "offline_fallback"
        else:
            intent = "general_question"
        
        state["intent"] = intent
        
        if self.telemetry:
            await self.telemetry.emit("intent_classified", {
                "user_id": state["user_id"],
                "intent": intent
            })
        
        return state
    
    async def retrieve_context_node(self, state: ConversationState) -> ConversationState:
        """
        Node 3: Context Retrieval
        Search vector DB, check semantic cache
        """
        logger.info(f"🔍 Retrieving context for intent: {state['intent']}")
        
        if self.telemetry:
            await self.telemetry.emit("retrieval_start", {
                "intent": state["intent"],
                "query": state["query"][:100]
            })
        
        # TODO: Implement actual vector DB search (Pinecone)
        # TODO: Check Redis semantic cache first
        
        # Mock retrieved documents
        retrieved_docs = [
            {
                "content": "PM-KISAN is a Central Sector scheme providing income support to farmer families.",
                "source": "PM_Kisan_Guidelines.pdf",
                "confidence": 0.92
            },
            {
                "content": "Eligible farmers receive ₹6000 per year in three installments.",
                "source": "PM_Kisan_FAQ.pdf",
                "confidence": 0.88
            }
        ]
        
        state["retrieved_docs"] = retrieved_docs
        state["sources"] = [doc["source"] for doc in retrieved_docs]
        
        # Simulate cache hit for demo
        if "pm kisan" in state["query"].lower():
            if self.telemetry:
                await self.telemetry.emit("cache_hit", {
                    "query": state["query"],
                    "latency_ms": 12
                })
        
        return state
    
    async def generate_response_node(self, state: ConversationState) -> ConversationState:
        """
        Node 4: LLM Response Generation
        Generate short, voice-friendly answers
        """
        logger.info("🤖 Generating response...")
        
        if self.telemetry:
            await self.telemetry.emit("generation_start", {
                "intent": state["intent"],
                "docs_count": len(state.get("retrieved_docs", []))
            })
        
        # Build context from retrieved docs
        context = "\n".join([
            f"- {doc['content']}" 
            for doc in state.get("retrieved_docs", [])
        ])
        
        # Voice-optimized prompt
        system_prompt = f"""You are SatyaSetu, a helpful AI assistant for rural India.
Language: {state['language']}
Intent: {state['intent']}

CRITICAL RULES:
1. Keep answers SHORT (2-3 sentences max) - this is for VOICE output
2. Use simple language (8th grade level)
3. Be warm and trustworthy
4. If verifying scams, be clear and direct
5. Always cite sources when available

Context:
{context}
"""
        
        # TODO: Implement streaming response
        # For now, generate full response
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["query"]}
            ]
            
            # Mock response (TODO: Replace with actual LLM call)
            if state["intent"] == "scheme_lookup":
                response = "PM-KISAN provides ₹6000 per year to eligible farmers in three installments. You can check your status on the official PM-KISAN portal."
            elif state["intent"] == "scam_verify":
                response = "This appears to be a scam. Government schemes never ask for money upfront. Please report this to cybercrime.gov.in."
            else:
                response = "I can help you verify messages or learn about government schemes. What would you like to know?"
            
            state["response"] = response
            state["confidence"] = 0.85
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            state["response"] = "I'm having trouble right now. Please try again in a moment."
            state["confidence"] = 0.0
        
        return state
    
    async def post_process_node(self, state: ConversationState) -> ConversationState:
        """
        Node 5: Post-processing
        Output guardrails, simplification, translation
        """
        logger.info("✨ Post-processing response...")
        
        # Output guardrails
        response = state["response"]
        
        # Check for hallucination patterns
        if "I don't know" in response or "I'm not sure" in response:
            state["confidence"] = min(state["confidence"], 0.5)
        
        # Ensure no financial/legal advice
        if any(word in response.lower() for word in ["invest", "lawsuit", "legal action"]):
            response = "I cannot provide financial or legal advice. Please consult a professional."
            state["risk_flags"].append("attempted_advice")
        
        # Language translation (TODO: Implement Hindi translation)
        if state["language"] == "hi":
            # TODO: Translate to Hindi
            pass
        
        state["response"] = response
        state["timestamp"] = datetime.now().isoformat()
        
        if self.telemetry:
            await self.telemetry.emit("response_complete", {
                "user_id": state["user_id"],
                "confidence": state["confidence"],
                "response_length": len(response),
                "sources": state.get("sources", [])
            })
        
        return state
    
    # ==================== ROUTING FUNCTIONS ====================
    
    def _route_after_safety(self, state: ConversationState) -> str:
        """Route based on safety check result"""
        return "safe" if state["safe"] else "unsafe"
    
    def _route_after_intent(self, state: ConversationState) -> str:
        """Route based on intent (online vs offline)"""
        return "offline" if state["intent"] == "offline_fallback" else "online"
    
    # ==================== PUBLIC API ====================
    
    async def process_query(
        self, 
        user_id: str, 
        query: str, 
        language: str = "en",
        offline_mode: bool = False
    ) -> dict:
        """
        Main entry point for processing user queries
        Returns AI response with metadata
        """
        logger.info(f"📥 Processing query from {user_id}: {query[:50]}...")
        
        # Initialize state
        initial_state: ConversationState = {
            "user_id": user_id,
            "language": language,
            "query": query,
            "intent": "",
            "retrieved_docs": [],
            "response": "",
            "safe": True,
            "confidence": 0.0,
            "risk_flags": [],
            "sources": [],
            "messages": [HumanMessage(content=query)],
            "timestamp": datetime.now().isoformat(),
            "offline_mode": offline_mode
        }
        
        # Run through the graph
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "text": final_state["response"],
                "confidence": final_state["confidence"],
                "riskLevel": "high" if final_state["risk_flags"] else "low",
                "sources": final_state.get("sources", []),
                "riskFlags": final_state["risk_flags"],
                "intent": final_state["intent"],
                "timestamp": final_state["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "text": "I'm experiencing technical difficulties. Please try again.",
                "confidence": 0.0,
                "riskLevel": "high",
                "sources": [],
                "riskFlags": ["system_error"],
                "intent": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up AI Orchestrator...")
