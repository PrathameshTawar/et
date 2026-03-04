"""
API Routes for Module A: Automated Social Media Content Engine
FastAPI endpoints for content generation, scheduling, and analytics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json

from services_social_engine import (
    ContentGenerationService,
    SchedulingService,
    PromptOptimizationService,
    Platform
)

router = APIRouter(prefix="/api/social", tags=["social-media"])

# Services
content_service = ContentGenerationService()
scheduling_service = SchedulingService()
optimization_service = PromptOptimizationService()


# ============ Request/Response Models ============
class BrandProfileRequest(BaseModel):
    name: str
    keywords: List[str]
    tone: str  # "professional", "playful", "luxury", "bold"
    audience_persona: Dict
    platforms: List[str]
    brand_colors: Optional[List[str]] = None
    brand_description: Optional[str] = None


class ContentGenerationRequest(BaseModel):
    brand_id: str
    topic: str
    platforms: List[str]  # ["instagram", "linkedin", "twitter"]
    include_media: bool = False  # Generate images/videos
    campaign_goal: str = "engagement"


class PostScheduleRequest(BaseModel):
    brand_id: str
    platform: str
    caption: str
    hashtags: List[str]
    scheduled_time: Optional[datetime] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class EngagementFeedbackRequest(BaseModel):
    post_id: str
    platform: str
    likes: int
    comments: int
    shares: int
    clicks: int
    watch_time_seconds: Optional[float] = None


class ContentPackageResponse(BaseModel):
    brand_id: str
    topic: str
    platforms: Dict
    generated_at: str


# ============ Brand Management ============
@router.post("/brands/create")
async def create_brand(request: BrandProfileRequest):
    """Create a new brand profile for content generation"""
    
    brand = {
        "id": "brand_" + str(datetime.utcnow().timestamp()).replace(".", ""),
        "name": request.name,
        "keywords": request.keywords,
        "tone": request.tone,
        "audience_persona": request.audience_persona,
        "platforms": request.platforms,
        "brand_colors": request.brand_colors or [],
        "brand_description": request.brand_description,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # In production, save to database
    return {
        "status": "success",
        "brand": brand,
        "message": f"Brand '{request.name}' created successfully"
    }


@router.get("/brands/{brand_id}")
async def get_brand(brand_id: str):
    """Retrieve brand profile"""
    
    # In production, fetch from database
    return {
        "status": "success",
        "brand_id": brand_id,
        "message": "Brand profile retrieved"
    }


# ============ Content Generation ============
@router.post("/generate-content")
async def generate_content(request: ContentGenerationRequest):
    """Generate social media content for brand"""
    
    try:
        # Parse platforms
        platforms = [Platform(p) for p in request.platforms]
        
        # Generate content
        content_package = await content_service.generate_complete_content(
            brand_name="Your Brand",
            brand_keywords=["fitness", "wellness"],  # In production, fetch from brand_id
            tone="playful",
            audience_persona={"age": "25-35", "interests": ["health", "lifestyle"]},
            platforms=platforms,
            topic=request.topic,
            campaign_goal=request.campaign_goal
        )
        
        return {
            "status": "success",
            "content_package": content_package,
            "ready_for_review": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Post Scheduling ============
@router.post("/schedule-post")
async def schedule_post(request: PostScheduleRequest, background_tasks: BackgroundTasks):
    """Schedule a post for publishing"""
    
    try:
        platform = Platform(request.platform)
        
        scheduled = await scheduling_service.schedule_post(
            platform=platform,
            caption=request.caption,
            hashtags=request.hashtags,
            scheduled_time=request.scheduled_time,
            image_url=request.image_url,
            video_url=request.video_url
        )
        
        return {
            "status": "success",
            "scheduled_post": scheduled.get("scheduled_post"),
            "message": scheduled.get("message")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled-posts/{brand_id}")
async def get_scheduled_posts(brand_id: str):
    """Get all scheduled posts for a brand"""
    
    # In production, fetch from database
    return {
        "status": "success",
        "brand_id": brand_id,
        "scheduled_posts": [],
        "total": 0
    }


# ============ Engagement Metrics ============
@router.post("/track-engagement")
async def track_engagement(request: EngagementFeedbackRequest):
    """Track post engagement and update metrics"""
    
    try:
        # Calculate derived metrics
        engagement_rate = (
            (request.likes + request.comments + request.shares) / 1000
        ) * 100 if request.likes + request.comments + request.shares > 0 else 0
        
        ctr = (request.clicks / 1000) * 100 if request.clicks > 0 else 0
        
        metrics = {
            "post_id": request.post_id,
            "platform": request.platform,
            "likes": request.likes,
            "comments": request.comments,
            "shares": request.shares,
            "clicks": request.clicks,
            "watch_time_seconds": request.watch_time_seconds or 0,
            "engagement_rate": engagement_rate,
            "ctr": ctr,
            "tracked_at": datetime.utcnow().isoformat()
        }
        
        # Track in optimization service
        optimization_service.track_performance(request.post_id, metrics)
        
        return {
            "status": "success",
            "metrics": metrics,
            "message": "Engagement tracked successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/{post_id}")
async def get_engagement(post_id: str):
    """Get engagement metrics for a post"""
    
    # In production, fetch from database
    return {
        "status": "success",
        "post_id": post_id,
        "metrics": {
            "likes": 150,
            "comments": 24,
            "shares": 8,
            "ctr": 3.2
        }
    }


# ============ Analytics ============
@router.get("/analytics/platform/{platform}")
async def get_platform_analytics(platform: str):
    """Get analytics for a specific platform"""
    
    patterns = optimization_service.get_performance_patterns(Platform(platform))
    
    return {
        "status": "success",
        "platform": platform,
        "analytics": patterns
    }


@router.get("/analytics/brand/{brand_id}")
async def get_brand_analytics(brand_id: str):
    """Get comprehensive analytics for brand"""
    
    return {
        "status": "success",
        "brand_id": brand_id,
        "analytics": {
            "total_posts": 12,
            "avg_engagement_rate": 4.5,
            "best_performing_platform": "instagram",
            "total_reach": 45000,
            "total_impressions": 120000
        }
    }


# ============ Content Optimization ============
@router.post("/optimize-content")
async def optimize_content_based_on_feedback(
    post_id: str,
    engagement_metrics: EngagementFeedbackRequest
):
    """Refine content based on engagement performance"""
    
    try:
        optimized = await content_service.optimize_based_on_feedback(
            original_caption="Original post caption here",
            engagement_metrics={
                "likes": engagement_metrics.likes,
                "comments": engagement_metrics.comments,
                "shares": engagement_metrics.shares,
                "ctr": engagement_metrics.clicks,
                "engagement_rate": 3.5
            },
            brand_keywords=["fitness", "wellness"],
            tone="playful",
            topic="morning workout routine",
            platform=Platform(engagement_metrics.platform)
        )
        
        return {
            "status": "success",
            "optimization_result": optimized
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/auto-optimize/{brand_id}")
async def auto_optimize_templates(brand_id: str):
    """Auto-optimize content templates based on performance"""
    
    try:
        platforms = [Platform.INSTAGRAM, Platform.LINKEDIN, Platform.TWITTER]
        optimizations = []
        
        for platform in platforms:
            result = await optimization_service.auto_refine_template(
                platform=platform,
                brand_keywords=["fitness"],
                tone="playful"
            )
            optimizations.append(result)
        
        return {
            "status": "success",
            "brand_id": brand_id,
            "optimizations": optimizations,
            "message": "Templates optimized based on performance"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Multi-Platform Content ============
@router.post("/multi-platform-adapt")
async def adapt_content_for_platforms(
    original_content: str,
    target_platforms: List[str]
):
    """Adapt single content piece for multiple platforms"""
    
    return {
        "status": "success",
        "platforms": target_platforms,
        "adapted_content": {
            "instagram": {
                "caption": "Adapted for Instagram with emojis 😊",
                "hashtags": ["#fitness", "#wellness"]
            },
            "linkedin": {
                "caption": "Professional adaptation for LinkedIn",
                "hashtags": ["#business", "#professional"]
            },
            "twitter": {
                "caption": "Concise Twitter version - 280 chars",
                "hashtags": ["#trending"]
            }
        }
    }


# ============ Content Drafts & Approval Workflow ============
@router.get("/drafts/{brand_id}")
async def get_content_drafts(brand_id: str):
    """Get all draft content waiting for approval"""
    
    return {
        "status": "success",
        "brand_id": brand_id,
        "drafts": [
            {
                "id": "draft_1",
                "topic": "New product launch",
                "platforms": ["instagram", "linkedin"],
                "status": "pending_review",
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1
    }


@router.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str):
    """Approve a draft and schedule for publishing"""
    
    return {
        "status": "success",
        "draft_id": draft_id,
        "message": "Draft approved and scheduled"
    }


@router.post("/drafts/{draft_id}/reject")
async def reject_draft(draft_id: str, reason: str = ""):
    """Reject draft and request regeneration"""
    
    return {
        "status": "success",
        "draft_id": draft_id,
        "message": "Draft rejected. Ready for regeneration."
    }
