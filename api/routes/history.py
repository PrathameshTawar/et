"""
History API Routes
Handles user scan history retrieval from DynamoDB
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import logging

from core.dynamodb_service import get_dynamodb_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ScanRecord(BaseModel):
    user_id: str
    timestamp: str
    scan_type: str
    input_text: str
    verdict: str
    risk_level: str
    confidence_score: float
    response: str
    sources: List[dict] = []
    risk_flags: List[str] = []
    language: str = "hi"
    processing_time: float = 0.0


class SaveScanRequest(BaseModel):
    user_id: str
    scan_type: str = "text"
    input_text: str
    verdict: str
    risk_level: str
    confidence_score: float
    response: str
    sources: List[dict] = []
    risk_flags: List[str] = []
    language: str = "hi"
    processing_time: float = 0.0


@router.post("/save-scan", response_model=dict)
async def save_scan(request: SaveScanRequest):
    """Save a scan record to DynamoDB"""
    dynamodb = get_dynamodb_service()
    
    scan_data = {
        'scan_type': request.scan_type,
        'input_text': request.input_text,
        'verdict': request.verdict,
        'risk_level': request.risk_level,
        'confidence_score': request.confidence_score,
        'response': request.response,
        'sources': request.sources,
        'risk_flags': request.risk_flags,
        'language': request.language,
        'processing_time': request.processing_time
    }
    
    success = await dynamodb.save_scan(request.user_id, scan_data)
    
    if success:
        return {"success": True, "message": "Scan saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save scan")


@router.get("/history/{user_id}", response_model=List[ScanRecord])
async def get_user_history(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get scan history for a specific user"""
    dynamodb = get_dynamodb_service()
    
    history = await dynamodb.get_user_history(user_id, limit)
    
    return history


@router.get("/history", response_model=List[ScanRecord])
async def get_recent_scans(limit: int = Query(default=100, ge=1, le=500)):
    """Get recent scans across all users"""
    dynamodb = get_dynamodb_service()
    
    scans = await dynamodb.get_recent_scans(limit)
    
    return scans


@router.delete("/history/{user_id}/{timestamp}")
async def delete_scan(user_id: str, timestamp: str):
    """Delete a specific scan record"""
    dynamodb = get_dynamodb_service()
    
    success = await dynamodb.delete_scan(user_id, timestamp)
    
    if success:
        return {"success": True, "message": "Scan deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete scan")
