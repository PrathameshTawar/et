"""
AWS Services for SatyaSetu
Amazon Transcribe (STT), Amazon Polly (TTS), Amazon Textract (OCR)
"""

import asyncio
import logging
import boto3
import time
import json
import tempfile
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any

from config import settings
from core.services import STTService, TTSService, VisionService
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class AWSSTTService(STTService):
    """Amazon Transcribe STT service - supports Hindi (hi-IN), Indian English (en-IN)"""
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, 
                 aws_region: str = "ap-south-1", s3_bucket: str = None):
        self.transcribe = boto3.client(
            'transcribe',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.s3_bucket = s3_bucket
        self.aws_region = aws_region
    
    # Language code mapping for AWS Transcribe
    LANGUAGE_CODES = {
        "hi": "hi-IN",  # Hindi
        "en": "en-IN",  # Indian English
        "bn": "bn-IN",  # Bengali (India)
        "ta": "ta-IN",  # Tamil
        "te": "te-IN",  # Telugu
        "mr": "mr-IN",  # Marathi
        "gu": "gu-IN",  # Gujarati
        "kn": "kn-IN",  # Kannada
        "ml": "ml-IN",  # Malayalam
    }
    
    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        try:
            # Map language to AWS code
            lang_code = self.LANGUAGE_CODES.get(language, "hi-IN")
            
            job_name = f"satyasetu-{int(time.time())}"
            
            # If S3 bucket is configured, upload audio to S3
            if self.s3_bucket:
                # Determine file format
                audio_format = "webm" if len(audio_data) > 0 else "ogg"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                try:
                    s3_key = f"audio/{job_name}.{audio_format}"
                    self.s3.upload_file(tmp_path, self.s3_bucket, s3_key)
                    uri = f"s3://{self.s3_bucket}/{s3_key}"
                finally:
                    os.unlink(tmp_path)
            else:
                raise ExternalServiceError("stt", "S3 bucket not configured for AWS Transcribe")
            
            # Start transcription job
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': uri},
                MediaFormat=audio_format,
                LanguageCode=lang_code
            )
            
            # Polling for completion
            transcript = ""
            for _ in range(30):
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status == 'COMPLETED':
                    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    res = requests.get(transcript_uri)
                    transcript = res.json()['results']['transcripts'][0]['transcript']
                    break
                elif job_status == 'FAILED':
                    raise ExternalServiceError("stt", "AWS Transcribe failed")
                await asyncio.sleep(2)
            
            return transcript or "Transcription timed out."
            
        except Exception as e:
            logger.error(f"STT failed: {e}")
            raise ExternalServiceError("stt", str(e))


class AWSTTSService(TTSService):
    """Amazon Polly TTS service - supports Hindi voices (Kajal, Aditi)"""
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, 
                 aws_region: str = "ap-south-1"):
        self.polly = boto3.client(
            'polly',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        # Voice mappings for Indian languages
        self.VOICE_MAPPING = {
            "hi": {"voice_id": "Kajal", "language_code": "hi-IN"},  # Hindi
            "en": {"voice_id": "Aditi", "language_code": "en-IN"},  # Indian English
            "mr": {"voice_id": "Kajal", "language_code": "hi-IN"},  # Marathi (uses Hindi voice)
            "bn": {"voice_id": "Kajal", "language_code": "hi-IN"},  # Bengali
            "ta": {"voice_id": "Kajal", "language_code": "hi-IN"},  # Tamil
            "te": {"voice_id": "Kajal", "language_code": "hi-IN"},  # Telugu
        }
    
    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "default") -> bytes:
        try:
            # Get voice configuration
            voice_config = self.VOICE_MAPPING.get(language, {"voice_id": "Kajal", "language_code": "hi-IN"})
            
            # Use custom voice_id if provided and not "default"
            actual_voice_id = voice_id if voice_id != "default" else voice_config["voice_id"]
            language_code = voice_config["language_code"]
            
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=actual_voice_id,
                Engine='neural',  # Neural engine for more natural voices
                LanguageCode=language_code
            )
            
            if "AudioStream" in response:
                return response['AudioStream'].read()
            else:
                raise ExternalServiceError("tts", "No audio stream returned")
                
        except Exception as e:
            logger.error(f"AWS Polly synthesis failed: {e}")
            raise ExternalServiceError("tts", str(e))


class AWSTextractService(VisionService):
    """Amazon Textract OCR service - supports Devanagari (Hindi/Marathi)"""
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, 
                 aws_region: str = "ap-south-1"):
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
    
    async def analyze_image(self, image_data: bytes, prompt: str = "Extract and analyze text from this image for potential scams.") -> str:
        try:
            # Detect document text (OCR)
            response = self.textract.detect_document_text(
                Document={'Bytes': image_data}
            )
            
            # Extract text from blocks
            extracted_lines = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    extracted_lines.append(block['Text'])
            
            extracted_text = '\n'.join(extracted_lines)
            
            # If prompt asks for analysis, return both OCR and analysis
            if prompt and prompt != "Extract and analyze text from this image for potential scams.":
                return f"Extracted Text:\n{extracted_text}\n\nAnalysis: {prompt}"
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"AWS Textract OCR failed: {e}")
            raise ExternalServiceError("vision", str(e))
    
    async def analyze_document(self, image_data: bytes) -> dict:
        """Advanced analysis for forms and tables"""
        try:
            response = self.textract.analyze_document(
                Document={'Bytes': image_data},
                FeatureTypes=["FORMS", "TABLES"]
            )
            
            # Extract key-value pairs and table data
            forms = {}
            tables = []
            
            for block in response['Blocks']:
                if block['BlockType'] == 'KEY_VALUE_SET':
                    key = block.get('Key', '')
                    value = block.get('Value', '')
                    if key and value:
                        forms[key] = value
            
            # Return structured data
            return {
                "text": '\n'.join([b['Text'] for b in response['Blocks'] if b['BlockType'] == 'LINE']),
                "forms": forms,
                "tables": tables
            }
        except Exception as e:
            logger.error(f"AWS Textract analyze_document failed: {e}")
            raise ExternalServiceError("vision", str(e))


# Factory functions for AWS services

def create_aws_stt_service() -> Optional[STTService]:
    """Create AWS Transcribe service if credentials are configured"""
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET:
        return AWSSTTService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION,
            s3_bucket=settings.AWS_S3_BUCKET
        )
    return None


def create_aws_tts_service() -> Optional[TTSService]:
    """Create AWS Polly service if credentials are configured"""
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        return AWSTTSService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION
        )
    return None


def create_aws_vision_service() -> Optional[VisionService]:
    """Create AWS Textract service if credentials are configured"""
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        return AWSTextractService(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION
        )
    return None
