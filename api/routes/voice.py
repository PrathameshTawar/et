"""
Voice API Routes
Handles voice input, STT, TTS, and AI processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

from core.validators import VoiceInputValidator, validate_audio_file
from core.exceptions import ValidationError, VoiceProcessingError

logger = logging.getLogger(__name__)
router = APIRouter()
ai_orchestrator = None
telemetry_manager = None


def _get_services():
    """Resolve shared services with module-level override support for tests."""
    global ai_orchestrator, telemetry_manager
    if ai_orchestrator is None or telemetry_manager is None:
        from main import ai_orchestrator as main_orchestrator, telemetry_manager as main_telemetry
        ai_orchestrator = ai_orchestrator or main_orchestrator
        telemetry_manager = telemetry_manager or main_telemetry
    return ai_orchestrator, telemetry_manager

class VoiceResponse(BaseModel):
    success: bool
    transcribed_text: Optional[str] = None
    intent: Optional[str] = None
    response: str
    audio_url: Optional[str] = None
    verdict: Optional[str] = None
    risk_level: Optional[str] = None
    risk_flags: Optional[list] = None
    sources: Optional[list] = None
    confidence_score: Optional[float] = None
    processing_time: float
    error: Optional[str] = None

@router.post("/process-audio", response_model=VoiceResponse)
async def process_audio(
    audio: UploadFile = File(...),
    user_id: Optional[str] = "anonymous"
):
    """Process uploaded audio file through AI pipeline"""
    
    ai_service, telemetry = _get_services()
    
    try:
        # Validate audio file
        validate_audio_file(audio)
        
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise ValidationError("audio_file", "Empty audio file")
        
        await telemetry.emit("audio_upload_received", {
            "user_id": user_id,
            "file_size": len(audio_data),
            "content_type": audio.content_type
        })
        
        # Process through AI orchestrator
        result = await ai_service.process_voice_input(audio_data, user_id)
        
        if result["success"]:
            return VoiceResponse(
                success=True,
                transcribed_text=result.get("transcribed_text"),
                intent=result.get("intent"),
                response=result.get("response", ""),
                verdict=result.get("verdict"),
                risk_level=result.get("risk_level"),
                risk_flags=result.get("risk_flags"),
                sources=result.get("sources"),
                confidence_score=result.get("confidence_score"),
                processing_time=result.get("processing_time", 0.0)
            )
        else:
            return VoiceResponse(
                success=False,
                response="",
                processing_time=0.0,
                error=result.get("error")
            )
            
    except ValidationError as e:
        logger.warning(f"Validation error in audio processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")
    except Exception as e:
        logger.error(f"Unexpected error in audio processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/process-text", response_model=VoiceResponse)
async def process_text(query: VoiceInputValidator):
    """Process text input through AI pipeline (for testing)"""
    ai_service, telemetry = _get_services()
    
    try:
        await telemetry.emit("text_input_received", {
            "user_id": query.user_id,
            "text_length": len(query.text),
            "language": query.language
        })
        
        # Mock audio data for text input
        mock_audio = query.text.encode('utf-8')
        
        # Process through orchestrator
        result = await ai_service.process_voice_input(query.text.encode("utf-8"), query.user_id)
        
        if result["success"]:
            return VoiceResponse(
                success=True,
                transcribed_text=query.text,
                intent=result.get("intent"),
                response=result.get("response", ""),
                verdict=result.get("verdict"),
                risk_level=result.get("risk_level"),
                risk_flags=result.get("risk_flags"),
                sources=result.get("sources"),
                confidence_score=result.get("confidence_score"),
                processing_time=result.get("processing_time", 0.0)
            )
        else:
            return VoiceResponse(
                success=False,
                response="",
                processing_time=0.0,
                error=result.get("error")
            )
            
    except ValidationError as e:
        logger.warning(f"Validation error in text processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")
    except Exception as e:
        logger.error(f"Unexpected error in text processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/process-image", response_model=VoiceResponse)
async def process_image(
    image: UploadFile = File(...),
    user_id: Optional[str] = "anonymous"
):
    """Process uploaded image for OCR and scam analysis"""
    
    ai_service, telemetry = _get_services()
    
    try:
        image_data = await image.read()
        
        await telemetry.emit("image_upload_received", {
            "user_id": user_id,
            "file_size": len(image_data),
            "content_type": image.content_type
        })
        
        # Process through orchestrator
        result = await ai_service.process_image_input(image_data, user_id)
        
        if result["success"]:
            return VoiceResponse(
                success=True,
                transcribed_text=result.get("transcribed_text"),
                intent=result.get("intent"),
                response=result.get("response", ""),
                verdict=result.get("verdict"),
                risk_level=result.get("risk_level"),
                risk_flags=result.get("risk_flags"),
                sources=result.get("sources"),
                confidence_score=result.get("confidence_score"),
                processing_time=result.get("processing_time", 0.0)
            )
        else:
            return VoiceResponse(
                success=False,
                response="",
                processing_time=0.0,
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Error in image processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def voice_health():
    """Voice service health check"""
    ai_service, _ = _get_services()
    
    try:
        is_healthy = ai_service.is_initialized
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "services": {
                "stt": "mock_ready",  # TODO: Check actual STT service
                "tts": "mock_ready",  # TODO: Check actual TTS service
                "ai_orchestrator": "ready" if is_healthy else "not_ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


class TextQueryRequest(BaseModel):
    query: str
    language: str = "en"
    user_id: str = "user123"


class TextQueryResponse(BaseModel):
    verdict: str
    confidence: float
    risk_level: str
    explanation: str
    risk_flags: list
    sources: list
    processing_time: float


@router.post("/query", response_model=TextQueryResponse)
async def text_query(request: TextQueryRequest):
    """Process text query and return scam verdict"""
    import time
    from orchestrator import run_orchestration
    
    try:
        start_time = time.time()
        
        # Run orchestration pipeline
        state = await run_orchestration(
            user_id=request.user_id,
            query=request.query,
            language=request.language
        )
        
        processing_time = time.time() - start_time
        
        return TextQueryResponse(
            verdict=state.verdict or "UNCERTAIN",
            confidence=state.meta.get("confidence", 0.5),
            risk_level=state.meta.get("risk_level", "MEDIUM"),
            explanation=state.response or "Unable to verify",
            risk_flags=state.meta.get("risk_flags", []),
            sources=state.meta.get("sources", []),
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error in text query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
