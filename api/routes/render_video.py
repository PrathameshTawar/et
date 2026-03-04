"""
Render video API: script JSON -> final reel MP4 URL.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.media_pipeline import MediaPipelineError, MediaPipelineService

router = APIRouter()
pipeline = MediaPipelineService()


class SceneInput(BaseModel):
    text: str
    duration_sec: Optional[float] = None


class RenderVideoRequest(BaseModel):
    script_text: Optional[str] = None
    scenes: List[SceneInput] = Field(default_factory=list)
    template_video: Optional[str] = None
    background_music: Optional[str] = None
    voice_id: str = "Joanna"
    language_code: str = "en-US"
    polly_engine: str = "neural"
    s3_key_prefix: str = "renders"
    mock_tts: bool = False
    skip_s3_upload: bool = False


@router.post("/render-video")
async def render_video(request: RenderVideoRequest) -> Dict[str, Any]:
    try:
        result = await asyncio.to_thread(pipeline.render, request.model_dump())
        return result
    except MediaPipelineError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "step": exc.step,
                "message": str(exc),
                "details": exc.details,
            },
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "step": "unhandled",
                "message": str(exc),
            },
        ) from exc
