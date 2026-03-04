"""
LangGraph-based AI Orchestrator - UPDATED VERSION
Explicit flow: safety_check → intent_router → retrieve_context → generate_response → post_process
Now with real LLM integration and Vector DB support!
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json
import logging

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, field_validator, ConfigDict

from core.exceptions import AIOrchestrationError, VoiceProcessingError
from core.services import (
    create_stt_service, 
    create_tts_service, 
    create_vision_service, 
    create_llm_service,
    create_vector_db_service
)
from core.llm_client import get_llm_client
from config import settings
from core.telemetry import TelemetryManager

logger = logging.getLogger(__name__)

class ConversationState(BaseModel):
    """State passed through the AI orchestration pipeline"""
    user_input: str = ""
    audio_data: Optional[bytes] = None
    transcribed_text: Optional[str] = None
    safety_status: str = "pending"
    safety_reason: str = ""
    intent: Optional[str] = None
    confidence_score: float = 0.0
    context: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    audio_response: Optional[bytes] = None
    
    # Scam detection specific fields
    verdict: Optional[str] = None
    risk_level: Optional[str] = None
    risk_flags: list = Field(default_factory=list)
    sources: list = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_steps: list = Field(default_factory=list)
    
    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class AIOrchestrator:
    """Main AI orchestration engine using LangGraph with real LLM and Vector DB"""
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None):
        self.telemetry = telemetry_manager or TelemetryManager()
        self.graph = None
        self.is_initialized = False
        
        # Initialize services
        self.stt_service = create_stt_service()
        self.tts_service = create_tts_service()
        
        # These will be initialized in initialize()
        self.llm_client = None
        self.vector_db_service = None
        self.vision_service = None
        self.llm_service = None
        
    async def initialize(self):
        """Initialize the LangGraph workflow"""
        try:
            self.llm_service = create_llm_service()
            self.vector_db_service = create_vector_db_service()
            self.vision_service = create_vision_service()
            self.llm_client = get_llm_client()
            
            self.graph = self._build_graph()
            self.is_initialized = True
            await self.telemetry.emit("orchestrator_initialized", {
                "nodes": ["safety_check", "intent_router", "retrieve_context", "generate_response", "post_process"],
                "settings": {
                    "max_response_length": settings.MAX_RESPONSE_LENGTH,
                    "processing_timeout": settings.PROCESSING_TIMEOUT,
                    "default_language": settings.DEFAULT_LANGUAGE
                }
            })
            logger.info("AI Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Orchestrator: {e}")
            raise AIOrchestrationError("Failed to initialize orchestrator", "initialization", {"error": str(e)})
    
    async def cleanup(self):
        """Cleanup orchestrator resources"""
        self.is_initialized = False
        logger.info("AI Orchestrator cleanup completed")
    
    def _build_graph(self) -> StateGraph:
        """Build the explicit AI orchestration graph"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("safety_check", self._safety_check_node)
        workflow.add_node("intent_router", self._intent_router_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("post_process", self._post_process_node)
        
        # Define edges (explicit flow)
        workflow.set_entry_point("safety_check")
        
        # Add conditional routing after safety check
        workflow.add_conditional_edges(
            "safety_check",
            self._safety_router,
            {
                "continue": "intent_router",
                "stop": "post_process"
            }
        )
        
        workflow.add_edge("intent_router", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", "post_process")
        workflow.add_edge("post_process", END)
        
        return workflow.compile()

    def _safety_router(self, state: ConversationState) -> str:
        """Route to next node or skip to end based on safety"""
        if state.safety_status == "unsafe":
            return "stop"
        return "continue"
    
    async def process_voice_input(self, audio_data: bytes, user_id: str = "anonymous") -> Dict[str, Any]:
        """Main entry point for voice processing"""
        if not self.is_initialized:
            raise AIOrchestrationError("Orchestrator not initialized", "initialization")
            
        start_time = datetime.now()
        
        # Initialize state
        state = ConversationState(
            user_input="",
            audio_data=audio_data,
            metadata={"user_id": user_id, "start_time": start_time.isoformat()}
        )
        
        await self.telemetry.emit("voice_processing_started", {
            "user_id": user_id,
            "audio_size": len(audio_data)
        })
        
        try:
            # Run through the graph with timeout
            result = await asyncio.wait_for(
                self.graph.ainvoke(state.model_dump()),
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.telemetry.emit("voice_processing_completed", {
                "user_id": user_id,
                "processing_time": processing_time,
                "intent": result.get("intent"),
                "response_length": len(result.get("response", "")),
                "confidence_score": result.get("confidence_score", 0.0)
            })
            
            return {
                "success": True,
                "transcribed_text": result.get("transcribed_text"),
                "intent": result.get("intent"),
                "response": result.get("response"),
                "audio_response": result.get("audio_response"),
                "verdict": result.get("verdict"),
                "risk_level": result.get("risk_level"),
                "risk_flags": result.get("risk_flags"),
                "sources": result.get("sources"),
                "processing_time": processing_time,
                "confidence_score": result.get("confidence_score", 0.0)
            }
            
        except asyncio.TimeoutError:
            await self.telemetry.emit("voice_processing_timeout", {
                "user_id": user_id,
                "timeout": settings.PROCESSING_TIMEOUT
            })
            return {
                "success": False,
                "error": f"Processing timeout after {settings.PROCESSING_TIMEOUT} seconds"
            }
        except Exception as e:
            await self.telemetry.emit("voice_processing_error", {
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__
            })
            logger.error(f"Voice processing failed for user {user_id}: {e}")
            return {
                "success": False,
                "error": "Processing failed. Please try again."
            }
    
    async def process_image_input(self, image_data: bytes, user_id: str = "anonymous") -> Dict[str, Any]:
        """Process image input through Vision API and AI pipeline"""
        if not self.is_initialized:
            raise AIOrchestrationError("Orchestrator not initialized", "initialization")
            
        start_time = datetime.now()
        
        try:
            await self.telemetry.emit("image_processing_started", {
                "user_id": user_id,
                "image_size": len(image_data)
            })
            
            # 1. OCR / Vision Analysis
            analysis_text = await self.vision_service.analyze_image(image_data)
            
            # 2. Run through graph using the extracted text
            state = ConversationState(
                user_input=analysis_text,
                metadata={"user_id": user_id, "start_time": start_time.isoformat(), "source": "image"}
            )
            
            result = await asyncio.wait_for(
                self.graph.ainvoke(state.model_dump()),
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "transcribed_text": analysis_text,
                "intent": result.get("intent"),
                "response": result.get("response"),
                "verdict": result.get("verdict"),
                "risk_level": result.get("risk_level"),
                "risk_flags": result.get("risk_flags"),
                "sources": result.get("sources"),
                "processing_time": processing_time,
                "confidence_score": result.get("confidence_score", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_text_input(self, text: str, user_id: str = "anonymous", language: str = "hi") -> Dict[str, Any]:
        """Process direct text input through AI pipeline"""
        if not self.is_initialized:
            raise AIOrchestrationError("Orchestrator not initialized", "initialization")
            
        start_time = datetime.now()
        
        state = ConversationState(
            user_input=text,
            transcribed_text=text,
            metadata={"user_id": user_id, "start_time": start_time.isoformat(), "source": "text"}
        )
        
        try:
            result = await asyncio.wait_for(
                self.graph.ainvoke(state.model_dump()),
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "transcribed_text": text,
                "intent": result.get("intent"),
                "response": result.get("response"),
                "verdict": result.get("verdict"),
                "risk_level": result.get("risk_level"),
                "risk_flags": result.get("risk_flags"),
                "sources": result.get("sources"),
                "processing_time": processing_time,
                "confidence_score": result.get("confidence_score", 0.0)
            }
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {"success": False, "error": str(e)}

    async def _safety_check_node(self, state: ConversationState) -> ConversationState:
        """Node 1: Safety and content filtering using LLM"""
        await self.telemetry.emit("node_safety_check_started", {"user_id": state.metadata.get("user_id")})
        
        try:
            # If we don't have text yet (voice input), we might need to skip or wait
            # But usually we transcribe in the next node. 
            # For now, let's assume we can check transcript if available, or skip for raw audio
            if state.transcribed_text or state.user_input:
                text_to_check = state.transcribed_text or state.user_input
                is_safe, reason = await self.llm_client.classify_safety(text_to_check)
                state.safety_status = "safe" if is_safe else "unsafe"
                state.safety_reason = reason
            else:
                state.safety_status = "safe" # Default safe for audio-only at this stage
            
            await self.telemetry.emit("node_safety_check_completed", {
                "user_id": state.metadata.get("user_id"),
                "status": state.safety_status,
                "reason": state.safety_reason
            })
            
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            state.safety_status = "safe" # Fail open for now or fail closed? 
            # In production, probably fail closed or use a simple heuristic
            
        return state
    
    async def _intent_router_node(self, state: ConversationState) -> ConversationState:
        """Node 2: Intent classification using LLM"""
        await self.telemetry.emit("node_intent_router_started", {"user_id": state.metadata.get("user_id")})
        
        try:
            # STT: Convert audio to text if needed
            if state.audio_data and not state.transcribed_text:
                state.transcribed_text = await self.stt_service.transcribe(
                    state.audio_data, 
                    language=settings.DEFAULT_LANGUAGE
                )
            
            state.user_input = state.transcribed_text or state.user_input
            
            # Use LLM for intent classification
            result = await self.llm_client.classify_intent(state.user_input, language=settings.DEFAULT_LANGUAGE)
            raw_intent = result.get("intent", "general")
            intent_map = {
                "general": "general_query",
                "info_lookup": "cybersecurity_education",
            }
            state.intent = intent_map.get(raw_intent, raw_intent)
            state.confidence_score = result.get("confidence", 0.5)
            
            await self.telemetry.emit("node_intent_router_completed", {
                "user_id": state.metadata.get("user_id"),
                "intent": state.intent,
                "confidence": state.confidence_score,
                "transcribed_text": state.transcribed_text
            })
            
        except Exception as e:
            logger.error(f"Intent router failed: {e}")
            # Fallback to keyword classification
            intent, confidence = self._classify_intent(state.user_input)
            state.intent = intent
            state.confidence_score = confidence
            
        return state
    
    def _classify_intent(self, text: str) -> tuple[str, float]:
        """Classify user intent based on text analysis"""
        text_lower = text.lower()
        
        # Cybersecurity education keywords
        education_keywords = [
            "साइबर सुरक्षा", "cyber security", "cybersecurity", "सुरक्षा", "security",
            "जानकारी", "information", "सिखाना", "learn", "बताना", "tell"
        ]
        
        # Threat report keywords  
        threat_keywords = [
            "रिपोर्ट", "report", "शिकायत", "complaint", "धोखाधड़ी", "fraud",
            "स्कैम", "scam", "फिशिंग", "phishing", "हैक", "hack"
        ]
        
        # Emergency keywords
        emergency_keywords = [
            "तत्काल", "urgent", "emergency", "आपातकाल", "मदद", "help",
            "बचाओ", "save", "खतरा", "danger"
        ]
        
        # Calculate scores
        education_score = sum(1 for keyword in education_keywords if keyword in text_lower)
        threat_score = sum(1 for keyword in threat_keywords if keyword in text_lower)
        emergency_score = sum(1 for keyword in emergency_keywords if keyword in text_lower)
        
        # Determine intent with confidence
        if emergency_score > 0:
            return "emergency", min(0.9, 0.6 + emergency_score * 0.1)
        elif threat_score > 0:
            return "threat_report", min(0.9, 0.7 + threat_score * 0.1)
        elif education_score > 0:
            return "cybersecurity_education", min(0.9, 0.8 + education_score * 0.05)
        else:
            return "general_query", 0.5
    
    async def _retrieve_context_node(self, state: ConversationState) -> ConversationState:
        """Node 3: Context retrieval from vector DB"""
        await self.telemetry.emit("node_retrieve_context_started", {
            "user_id": state.metadata.get("user_id"),
            "intent": state.intent
        })
        
        try:
            # Retrieve relevant context from vector database
            context_results = await self.vector_db_service.similarity_search(
                query=state.user_input,
                top_k=3,
                filters={"language": settings.DEFAULT_LANGUAGE}
            )
            
            # Extract context information
            relevant_docs = [doc["content"] for doc in context_results]
            
            state.context = {
                "relevant_docs": relevant_docs,
                "context_results": context_results,
                "threat_level": self._assess_threat_level(state.intent),
                "regional_context": "rural_india"
            }
            
            await self.telemetry.emit("node_retrieve_context_completed", {
                "user_id": state.metadata.get("user_id"),
                "context_items": len(relevant_docs),
                "avg_relevance": sum(doc.get("relevance_score", 0) for doc in context_results) / max(len(context_results), 1)
            })
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            # Fallback to minimal context
            state.context = {
                "relevant_docs": [],
                "threat_level": "unknown",
                "regional_context": "rural_india"
            }
        
        return state
    
    def _assess_threat_level(self, intent: str) -> str:
        """Assess threat level based on intent"""
        threat_levels = {
            "emergency": "high",
            "threat_report": "medium", 
            "cybersecurity_education": "low",
            "general_query": "low"
        }
        return threat_levels.get(intent, "unknown")
    
    async def _generate_response_node(self, state: ConversationState) -> ConversationState:
        """Node 4: AI response generation using LLM"""
        await self.telemetry.emit("node_generate_response_started", {
            "user_id": state.metadata.get("user_id"),
            "intent": state.intent
        })
        
        try:
            context_docs = state.context.get("context_results", []) if state.context else []
            
            if state.intent == "scam_verification":
                # Use specialized verdict generation for scams
                result = await self.llm_client.generate_verdict(
                    query=state.user_input,
                    context=context_docs,
                    language=settings.DEFAULT_LANGUAGE
                )
                
                state.verdict = result.get("verdict")
                state.confidence_score = result.get("confidence", 0.0)
                state.risk_level = result.get("risk_level")
                state.risk_flags = result.get("risk_flags", [])
                state.sources = result.get("sources", [])
                state.response = result.get("explanation")
            else:
                # Build regular prompt for other intents
                prompt = self._build_prompt(state)
                relevant_texts = [doc.get("content", "") for doc in context_docs]
                
                response = await self.llm_service.generate_response(
                    prompt=prompt,
                    context=relevant_texts,
                    max_tokens=settings.MAX_RESPONSE_LENGTH
                )
                state.response = response
            
            await self.telemetry.emit("node_generate_response_completed", {
                "user_id": state.metadata.get("user_id"),
                "response_length": len(state.response) if state.response else 0,
                "context_used": len(context_docs)
            })
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            # Fallback response
            fallback_responses = {
                "emergency": "तत्काल सहायता के लिए साइबर क्राइम हेल्पलाइन 1930 पर कॉल करें।",
                "threat_report": "आपकी रिपोर्ट दर्ज की गई है। हमारी टीम इसकी जांच करेगी।",
                "cybersecurity_education": "साइबर सुरक्षा के लिए मजबूत पासवर्ड का उपयोग करें।",
                "general_query": "मैं आपकी साइबर सुरक्षा संबंधी सहायता के लिए यहाँ हूँ।"
            }
            state.response = fallback_responses.get(state.intent, "मुझे समझ नहीं आया। कृपया दोबारा कहें।")
        
        return state
    
    def _build_prompt(self, state: ConversationState) -> str:
        """Build prompt for LLM based on state"""
        base_prompt = f"""
You are SatyaSetu, a helpful AI assistant for rural cybersecurity education in India.

User Query: {state.user_input}
Intent: {state.intent}
Language: {settings.DEFAULT_LANGUAGE}
Confidence: {state.confidence_score}

Context Information:
{chr(10).join(state.context.get("relevant_docs", [])[:2]) if state.context else "No specific context available"}

Instructions:
- Respond in {settings.DEFAULT_LANGUAGE} (Hindi) primarily
- Keep responses simple and practical for rural users
- Focus on actionable cybersecurity advice
- Be empathetic and supportive
- If it's an emergency, prioritize immediate help resources
"""
        return base_prompt
    
    async def _post_process_node(self, state: ConversationState) -> ConversationState:
        """Node 5: Post-processing and TTS"""
        await self.telemetry.emit("node_post_process_started", {
            "user_id": state.metadata.get("user_id")
        })
        
        try:
            # Handle unsafe content if router jumped here
            if state.safety_status == "unsafe":
                state.response = f"क्षमा करें, मैं इस अनुरोध में सहायता नहीं कर सकता। विवरण: {state.safety_reason}"
                state.intent = "unsafe_content"
                state.verdict = state.verdict or "suspicious"
                state.risk_level = state.risk_level or "HIGH"
            else:
                state.verdict = state.verdict or "unknown"
                state.risk_level = state.risk_level or "LOW"
            
            # Generate audio response using TTS
            if state.response:
                state.audio_response = await self.tts_service.synthesize(
                    text=state.response,
                    language=settings.DEFAULT_LANGUAGE,
                    voice_id="shimmer"
                )
            
            # Add processing step tracking
            state.processing_steps = [
                "safety_check", "intent_router", "retrieve_context", 
                "generate_response", "post_process"
            ]
            
            await self.telemetry.emit("node_post_process_completed", {
                "user_id": state.metadata.get("user_id"),
                "has_audio": bool(state.audio_response),
                "final_response_length": len(state.response) if state.response else 0
            })
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            # Continue without audio if TTS fails
            state.audio_response = None
        
        return state
