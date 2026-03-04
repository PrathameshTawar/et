"""
API Routes for Module B: Personalized News Feed
FastAPI endpoints for article ingestion, recommendations, and feed delivery
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from services_news_feed import (
    NLPPipeline,
    RecommendationEngine,
    UserProfileManager,
    FeedAssemblyService
)

router = APIRouter(prefix="/api/feed", tags=["news-feed"])

# Services
nlp_pipeline = NLPPipeline()
recommendation_engine = RecommendationEngine()
user_profile_manager = UserProfileManager()
feed_assembly_service = FeedAssemblyService()


# ============ Request/Response Models ============
class ArticleIngestionRequest(BaseModel):
    title: str
    body: str
    source: str
    source_url: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None


class UserBehaviorRequest(BaseModel):
    user_id: str
    article_id: str
    action: str  # "click", "read", "like", "share", "skip"
    read_time_seconds: int = 0
    scroll_depth: float = 0.0  # 0-1


class FeedRequest(BaseModel):
    user_id: str
    limit: int = 20
    offset: int = 0
    include_trending: bool = True


class ArticleResponse(BaseModel):
    id: str
    title: str
    source: str
    category: str
    recommendation_score: float
    is_exploratory: bool


# ============ Article Management ============
@router.post("/articles/ingest")
async def ingest_article(request: ArticleIngestionRequest):
    """Ingest and process new article"""
    
    try:
        # Extract tags via NLP
        tags_result = await nlp_pipeline.extract_tags(request.title, request.body)
        
        if tags_result.get("status") != "success":
            raise HTTPException(status_code=500, detail="NLP processing failed")
        
        # Generate embedding
        embedding_result = await nlp_pipeline.generate_embedding(request.body)
        
        article = {
            "id": f"article_{int(datetime.utcnow().timestamp() * 1000)}",
            "title": request.title,
            "body": request.body,
            "source": request.source,
            "source_url": request.source_url,
            "category": tags_result.get("category", request.category or "general"),
            "author": request.author,
            "published_date": request.published_date or datetime.utcnow(),
            "tags": tags_result.get("keywords", []),
            "topics": tags_result.get("topics", []),
            "entities": tags_result.get("entities", []),
            "sentiment": tags_result.get("sentiment", "neutral"),
            "embedding": embedding_result.get("embedding", []),
            "ingested_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "article": article,
            "message": "Article ingested and processed"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Retrieve article details"""
    
    # In production, fetch from database
    return {
        "status": "success",
        "article_id": article_id,
        "article": {
            "title": "Article Title",
            "source": "NewsSource",
            "category": "technology"
        }
    }


# ============ User Behavior Tracking ============
@router.post("/track-click")
async def track_user_behavior(request: UserBehaviorRequest):
    """Track user interaction with article"""
    
    try:
        behavior = {
            "user_id": request.user_id,
            "article_id": request.article_id,
            "action": request.action,
            "read_time_seconds": request.read_time_seconds,
            "scroll_depth": request.scroll_depth,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In production, save to database and update user profile
        
        return {
            "status": "success",
            "behavior": behavior,
            "message": "User behavior tracked"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile with interests and preferences"""
    
    # In production, fetch from database
    return {
        "status": "success",
        "user_id": user_id,
        "profile": {
            "interests": ["technology", "startup", "ai"],
            "engagement_preference": "high",
            "read_time_avg": 245,
            "category_preferences": {
                "technology": 0.4,
                "business": 0.3,
                "science": 0.3
            }
        }
    }


# ============ Personalized Feed ============
@router.post("/generate")
async def generate_personalized_feed(request: FeedRequest):
    """Generate personalized feed for user"""
    
    try:
        # Mock articles (in production, fetch from database)
        mock_articles = [
            {
                "id": "art_1",
                "title": "AI Breakthroughs in 2024",
                "body": "Recent developments in artificial intelligence...",
                "source": "TechCrunch",
                "category": "technology",
                "tags": ["ai", "machine-learning", "breakthroughs"],
                "topics": ["AI", "Tech"],
                "entities": ["OpenAI", "Google"],
                "sentiment": "positive",
                "embedding": [0.1] * 1536,
                "published_date": datetime.utcnow().isoformat()
            },
            {
                "id": "art_2",
                "title": "Startup Funding Trends",
                "body": "Latest trends in venture capital...",
                "source": "Crunchbase",
                "category": "business",
                "tags": ["startups", "funding", "vc"],
                "topics": ["Business", "Startups"],
                "entities": ["Sequoia", "Andreessen Horowitz"],
                "sentiment": "neutral",
                "embedding": [0.2] * 1536,
                "published_date": datetime.utcnow().isoformat()
            }
        ]
        
        # Mock user profile
        user_profile = {
            "user_id": request.user_id,
            "interests": ["technology", "startup", "ai"],
            "interests_embedding": [0.15] * 1536,
            "engagement_preference": "high",
            "read_time_avg": 245,
            "behavior_history": [
                {
                    "category": "technology",
                    "read_time_seconds": 300,
                    "article_tags": ["ai", "tech"]
                }
            ]
        }
        
        # Generate feed
        feed = await feed_assembly_service.generate_feed(
            user_id=request.user_id,
            articles=mock_articles,
            user_profile=user_profile,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "feed": feed.get("articles", []),
            "total_count": feed.get("total_count", 0),
            "metadata": feed.get("metadata", {}),
            "generated_at": feed.get("generated_at")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_feed(
    user_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_trending: bool = Query(True)
):
    """Get personalized feed for user"""
    
    # This is the main feed endpoint - integrates with above logic
    request = FeedRequest(
        user_id=user_id,
        limit=limit,
        offset=offset,
        include_trending=include_trending
    )
    
    return await generate_personalized_feed(request)


# ============ Trending Articles ============
@router.get("/trending")
async def get_trending_articles(limit: int = Query(10, ge=1, le=50)):
    """Get trending articles (not personalized)"""
    
    # In production, fetch trending from database based on engagement signals
    trending = [
        {
            "id": "trend_1",
            "title": "Breaking: AI Passes Major Benchmark",
            "source": "BBC",
            "category": "technology",
            "engagement_score": 0.95,
            "trending_rank": 1
        },
        {
            "id": "trend_2",
            "title": "Market Reaches All-Time High",
            "source": "Reuters",
            "category": "business",
            "engagement_score": 0.88,
            "trending_rank": 2
        }
    ]
    
    return {
        "status": "success",
        "trending": trending[:limit],
        "total": len(trending)
    }


# ============ Recommendations ============
@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get article recommendations for user"""
    
    return {
        "status": "success",
        "user_id": user_id,
        "recommendations": [
            {
                "id": "rec_1",
                "title": "Recommended Article",
                "reason": "Based on your interest in technology",
                "confidence": 0.92
            }
        ]
    }


# ============ Search & Filter ============
@router.get("/search")
async def search_articles(
    q: str = Query(...),
    category: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Search articles"""
    
    return {
        "status": "success",
        "query": q,
        "results": [],
        "total": 0
    }


@router.get("/by-category/{category}")
async def get_articles_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("latest", regex="^(latest|trending|engagement)$")
):
    """Get articles by category"""
    
    return {
        "status": "success",
        "category": category,
        "sort_by": sort_by,
        "articles": [],
        "total": 0
    }


# ============ User Preferences ============
@router.post("/preferences/{user_id}/interests")
async def update_user_interests(
    user_id: str,
    interests: List[str]
):
    """Update user interests"""
    
    return {
        "status": "success",
        "user_id": user_id,
        "interests": interests,
        "message": "Interests updated"
    }


@router.post("/preferences/{user_id}/engagement-level")
async def set_engagement_level(
    user_id: str,
    level: str  # "low", "medium", "high"
):
    """Set content engagement level"""
    
    return {
        "status": "success",
        "user_id": user_id,
        "engagement_level": level,
        "message": "Engagement level updated"
    }


@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user feed preferences"""
    
    return {
        "status": "success",
        "user_id": user_id,
        "preferences": {
            "interests": ["technology", "startup"],
            "engagement_level": "high",
            "trending_ratio": 0.2,
            "allow_exploration": True,
            "muted_sources": []
        }
    }


# ============ Analytics ============
@router.get("/analytics/user/{user_id}")
async def get_user_feed_analytics(user_id: str):
    """Get feed consumption analytics for user"""
    
    return {
        "status": "success",
        "user_id": user_id,
        "analytics": {
            "articles_read": 145,
            "avg_read_time": 245,
            "categories_engaged": ["technology", "business", "science"],
            "most_read_source": "TechCrunch",
            "engagement_trend": "increasing"
        }
    }


@router.get("/analytics/global")
async def get_global_feed_analytics():
    """Get global feed statistics"""
    
    return {
        "status": "success",
        "global_stats": {
            "total_articles": 50000,
            "avg_article_views": 1250,
            "top_categories": ["technology", "business", "health"],
            "trending_topics": ["AI", "startup", "crypto"],
            "user_engagement_rate": 0.68
        }
    }
