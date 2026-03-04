"""
Input validation utilities for SatyaSetu
Ensures data integrity and security
"""

import re
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field
from fastapi import HTTPException, UploadFile

from core.exceptions import ValidationError
from config import settings

class VoiceInputValidator(BaseModel):
    """Validator for voice input data"""
    text: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(default="anonymous", max_length=100)
    language: str = Field(default="hi", pattern=r"^(hi|en|bn|te|ta|mr|gu|kn|ml|or|pa)$")
    
    @field_validator('text')
    def validate_text_content(cls, v):
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v.strip())
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValidationError("text", "Potentially harmful content detected")
        
        return v
    
    @field_validator('user_id')
    def validate_user_id(cls, v):
        # Sanitize user ID
        v = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        return v or "anonymous"

def validate_audio_file(file: UploadFile) -> None:
    """Validate uploaded audio file"""
    
    # Check file size
    if hasattr(file, 'size') and file.size:
        max_size = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024  # Convert to bytes
        if file.size > max_size:
            raise ValidationError(
                "audio_file", 
                f"File size exceeds {settings.MAX_AUDIO_SIZE_MB}MB limit",
                file.size
            )
    
    # Check file type
    allowed_types = [
        'audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 
        'audio/webm', 'audio/m4a', 'audio/aac'
    ]
    
    if file.content_type not in allowed_types:
        raise ValidationError(
            "audio_file",
            f"Unsupported file type. Allowed: {', '.join(allowed_types)}",
            file.content_type
        )
    
    # Check filename
    if not file.filename:
        raise ValidationError("audio_file", "Filename is required")
    
    # Sanitize filename
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', file.filename)
    if not safe_filename:
        raise ValidationError("audio_file", "Invalid filename")

class AdminQueryValidator(BaseModel):
    """Validator for admin queries"""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    event_type: Optional[str] = Field(None, max_length=100)
    
    @field_validator('event_type')
    def validate_event_type(cls, v):
        if v:
            # Only allow alphanumeric and underscores
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValidationError("event_type", "Invalid event type format")
        return v

def validate_language_code(lang: str) -> str:
    """Validate and normalize language code"""
    supported_languages = {
        'hi': 'Hindi',
        'en': 'English', 
        'bn': 'Bengali',
        'te': 'Telugu',
        'ta': 'Tamil',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'or': 'Odia',
        'pa': 'Punjabi'
    }
    
    lang = lang.lower().strip()
    if lang not in supported_languages:
        raise ValidationError(
            "language", 
            f"Unsupported language. Supported: {list(supported_languages.keys())}"
        )
    
    return lang