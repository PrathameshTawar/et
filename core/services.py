"""
External service integrations for SatyaSetu
STT, TTS, Vector DB, and LLM services
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Any as AnyType
from abc import ABC, abstractmethod
from datetime import datetime

from config import settings
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class STTService(ABC):
    """Abstract Speech-to-Text service"""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        pass


class TTSService(ABC):
    """Abstract Text-to-Speech service"""

    @abstractmethod
    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "default") -> bytes:
        pass


class VectorDBService(ABC):
    """Abstract Vector Database service"""

    @abstractmethod
    async def similarity_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def upsert(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        pass


class LLMService(ABC):
    """Abstract Large Language Model service"""

    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[List[str]] = None, max_tokens: int = 500) -> str:
        pass


class VisionService(ABC):
    """Abstract Computer Vision / OCR service"""

    @abstractmethod
    async def analyze_image(self, image_data: bytes, prompt: str = "Extract and analyze text from this image for potential scams.") -> str:
        pass


# Real Implementations

import io
import base64
from openai import AsyncOpenAI
from pinecone import Pinecone


class WhisperSTTService(STTService):
    """OpenAI Whisper STT service"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"

            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
            return transcript.text
        except Exception as e:
            logger.error(f"Whisper STT transcription failed: {e}")
            raise ExternalServiceError("stt", str(e))


class OpenAITTSService(TTSService):
    """OpenAI TTS service"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "shimmer") -> bytes:
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice_id if voice_id != "default" else "shimmer",
                input=text
            )
            # response.read() returns bytes directly, not awaitable
            return response.read()
        except Exception as e:
            logger.error(f"OpenAI TTS synthesis failed: {e}")
            raise ExternalServiceError("tts", str(e))


class PineconeService(VectorDBService):
    """Pinecone Vector DB service"""

    def __init__(self, api_key: str, environment: str, index_name: str, openai_api_key: str):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.index = self.pc.Index(index_name)
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)

    async def _get_embedding(self, text: str) -> List[float]:
        response = await self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def similarity_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            vector = await self._get_embedding(query)
            pc_filter = filters if filters else {}

            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=pc_filter if pc_filter else None
            )

            # Handle Pinecone response - results.matches might be accessed differently
            matches: AnyType = getattr(results, 'matches', [])
            return [
                {
                    "content": match.metadata.get("text", match.metadata.get("content", "")),
                    "relevance_score": match.score,
                    "metadata": match.metadata
                }
                for match in matches
            ]
        except Exception as e:
            logger.error(f"Pinecone similarity search failed: {e}")
            raise ExternalServiceError("vector_db", str(e))

    async def upsert(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        try:
            vectors = []
            for i, text in enumerate(texts):
                embedding = await self._get_embedding(text)
                metadata = metadatas[i] if metadatas else {}
                metadata["text"] = text
                vector_id = ids[i] if ids else f"id_{i}_{datetime.now().timestamp()}"
                vectors.append((vector_id, embedding, metadata))

            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted {len(texts)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            raise ExternalServiceError("vector_db", str(e))


class OpenAILLMService(LLMService):
    """OpenAI LLM service wrapper for the orchestrator"""

    def __init__(self, api_key: str):
        from core.llm_client import LLMClient
        self.client = LLMClient(api_key=api_key)

    async def generate_response(self, prompt: str, context: Optional[List[str]] = None, max_tokens: int = 500) -> str:
        messages = [
            {"role": "system", "content": "You are SatyaSetu, a helpful AI assistant for rural cybersecurity education in India."},
            {"role": "user", "content": prompt}
        ]
        result = await self.client.get_response(messages, max_tokens=max_tokens)
        return result if result else ""


class OpenAIVisionService(VisionService):
    """OpenAI Vision service (GPT-4o)"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze_image(self, image_data: bytes, prompt: str = "Extract and analyze text from this image for potential scams.") -> str:
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            logger.error(f"OpenAI Vision analysis failed: {e}")
            raise ExternalServiceError("vision", str(e))


# Mock implementations for development/demo (keeping these as fallbacks)

class MockSTTService(STTService):
    """Mock STT service for development"""

    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        await asyncio.sleep(0.5)

        mock_transcriptions = {
            "hi": "मुझे साइबर सुरक्षा के बारे में जानकारी चाहिए",
            "en": "I need information about cybersecurity",
            "bn": "আমার সাইবার নিরাপত্তা সম্পর্কে তথ্য দরকার"
        }

        try:
            text_input = audio_data.decode('utf-8')
            if len(text_input) < 1000:
                return text_input
        except Exception:
            pass

        return mock_transcriptions.get(language, mock_transcriptions["hi"])


class MockTTSService(TTSService):
    """Mock TTS service for development"""

    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "default") -> bytes:
        await asyncio.sleep(0.3)
        return f"MOCK_AUDIO_DATA:{text[:50]}...".encode('utf-8')


class MockVectorDBService(VectorDBService):
    """Mock Vector DB service for development"""

    def __init__(self):
        self.knowledge_base = [
            {"content": "साइबर सुरक्षा के मूल सिद्धांत: मजबूत पासवर्ड का उपयोग करें।", "category": "cybersecurity_basics", "language": "hi", "score": 0.95},
            {"content": "Basic cybersecurity principles: Use strong passwords.", "category": "cybersecurity_basics", "language": "en", "score": 0.95}
        ]

    async def similarity_search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.2)
        return [{"content": doc["content"], "relevance_score": 0.9, "metadata": doc} for doc in self.knowledge_base[:top_k]]

    async def upsert(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        await asyncio.sleep(0.5)
        logger.info(f"[MOCK] Upserted {len(texts)} documents")
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            self.knowledge_base.append({"content": text, **metadata})


class MockLLMService(LLMService):
    """Mock LLM service for development"""

    async def generate_response(self, prompt: str, context: Optional[List[str]] = None, max_tokens: int = 500) -> str:
        await asyncio.sleep(0.8)
        return f"[MOCK RESPONSE] {prompt[:50]}..."


class MockVisionService(VisionService):
    """Mock Vision service for development"""

    async def analyze_image(self, image_data: bytes, prompt: str = "") -> str:
        await asyncio.sleep(1.0)
        return "This image appears to show a payment receipt for 5000 INR. It might be related to a lottery scam."


# Factory functions

def create_stt_service() -> STTService:
    """Create STT service based on configuration"""
    if settings.PREFERRED_STT == "aws" and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET:
        from core.aws_services import AWSSTTService
        return AWSSTTService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION,
            s3_bucket=settings.AWS_S3_BUCKET
        )
    if settings.OPENAI_API_KEY:
        return WhisperSTTService(settings.OPENAI_API_KEY)
    return MockSTTService()


def create_tts_service() -> TTSService:
    """Create TTS service based on configuration"""
    if settings.PREFERRED_TTS == "aws" and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        from core.aws_services import AWSTTSService
        return AWSTTSService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION
        )
    if settings.OPENAI_API_KEY:
        return OpenAITTSService(settings.OPENAI_API_KEY)
    return MockTTSService()


def create_vector_db_service() -> VectorDBService:
    """Create Vector DB service based on configuration"""
    if settings.PINECONE_API_KEY and settings.OPENAI_API_KEY:
        return PineconeService(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT or "us-east-1",
            index_name=settings.VECTOR_DB_INDEX,
            openai_api_key=settings.OPENAI_API_KEY
        )
    return MockVectorDBService()


def create_llm_service() -> LLMService:
    """Create LLM service based on configuration"""
    if settings.OPENAI_API_KEY:
        return OpenAILLMService(settings.OPENAI_API_KEY)
    return MockLLMService()


def create_vision_service() -> VisionService:
    """Create Vision service based on configuration"""
    if settings.PREFERRED_OCR == "aws" and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        from core.aws_services import AWSTextractService
        return AWSTextractService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION
        )
    if settings.OPENAI_API_KEY:
        return OpenAIVisionService(settings.OPENAI_API_KEY)
    return MockVisionService()
