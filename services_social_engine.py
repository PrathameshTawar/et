"""
Module A: Automated Social Media Content Engine
Content generation, scheduling, and feedback optimization
"""

import openai
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import asyncio
from enum import Enum

# Initialize OpenAI (should use environment variable)
openai.api_key = "${OPENAI_API_KEY}"

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"


class ContentGenerationService:
    """Service for AI-powered social media content generation"""
    
    def __init__(self):
        self.model = "gpt-4"
        self.temperature = 0.7
    
    async def generate_caption(
        self,
        brand_keywords: List[str],
        platform: Platform,
        topic: str,
        tone: str,
        audience_persona: Dict,
        cta: str = None,
    ) -> Dict:
        """Generate platform-specific caption with LLM"""
        
        from llm_templates import PLATFORM_TEMPLATES
        
        template = PLATFORM_TEMPLATES[platform.value]["caption_format"]
        
        prompt = template.format(
            brand_name="Your Brand",
            topic=topic,
            keywords=", ".join(brand_keywords),
            tone=tone,
            audience_persona=str(audience_persona),
            cta=cta or "Learn more"
        )
        
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media content expert. Generate engaging, platform-optimized captions that drive engagement and conversions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            caption = response.choices[0].message.content.strip()
            
            return {
                "status": "success",
                "caption": caption,
                "platform": platform.value,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "platform": platform.value
            }
    
    async def generate_hashtags(
        self,
        brand_keywords: List[str],
        platform: Platform,
        topic: str,
    ) -> Dict:
        """Generate platform-optimized hashtags"""
        
        from llm_templates import PLATFORM_TEMPLATES
        
        template = PLATFORM_TEMPLATES[platform.value]["hashtags"]
        
        prompt = template.format(
            topic=topic,
            brand_name="Your Brand",
            keywords=", ".join(brand_keywords)
        )
        
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a hashtag strategy expert. Generate relevant, trending hashtags that increase discoverability."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split('\n') if tag.strip()]
            
            return {
                "status": "success",
                "hashtags": hashtags,
                "count": len(hashtags),
                "platform": platform.value
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_complete_content(
        self,
        brand_name: str,
        brand_keywords: List[str],
        tone: str,
        audience_persona: Dict,
        platforms: List[Platform],
        topic: str,
        campaign_goal: str = "engagement"
    ) -> Dict:
        """Generate complete content package for multiple platforms"""
        
        content_package = {
            "brand": brand_name,
            "topic": topic,
            "campaign_goal": campaign_goal,
            "generated_at": datetime.utcnow().isoformat(),
            "platforms": {}
        }
        
        for platform in platforms:
            # Generate caption
            caption_result = await self.generate_caption(
                brand_keywords=brand_keywords,
                platform=platform,
                topic=topic,
                tone=tone,
                audience_persona=audience_persona
            )
            
            # Generate hashtags
            hashtags_result = await self.generate_hashtags(
                brand_keywords=brand_keywords,
                platform=platform,
                topic=topic
            )
            
            content_package["platforms"][platform.value] = {
                "caption": caption_result.get("caption", ""),
                "hashtags": hashtags_result.get("hashtags", []),
                "status": "ready_for_review"
            }
        
        return content_package
    
    async def optimize_based_on_feedback(
        self,
        original_caption: str,
        engagement_metrics: Dict,
        brand_keywords: List[str],
        tone: str,
        topic: str,
        platform: Platform
    ) -> Dict:
        """Refine content based on engagement performance"""
        
        from llm_templates import PROMPT_OPTIMIZATION_TEMPLATE, CAPTION_REFINEMENT_TEMPLATE
        
        # First, analyze what worked
        analysis_prompt = PROMPT_OPTIMIZATION_TEMPLATE.format(
            post_content=original_caption,
            platform=platform.value,
            likes=engagement_metrics.get("likes", 0),
            comments=engagement_metrics.get("comments", 0),
            shares=engagement_metrics.get("shares", 0),
            ctr=engagement_metrics.get("ctr", 0),
            engagement_rate=engagement_metrics.get("engagement_rate", 0),
            keywords=", ".join(brand_keywords),
            tone=tone
        )
        
        try:
            analysis_response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data-driven content strategist. Analyze performance and provide actionable improvements."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            analysis = analysis_response.choices[0].message.content
            
            # Now generate refined caption
            refinement_prompt = CAPTION_REFINEMENT_TEMPLATE.format(
                engagement_rate=engagement_metrics.get("engagement_rate", 0),
                original_caption=original_caption,
                performance_analysis=analysis,
                tone=tone,
                topic=topic,
                platform=platform.value,
                audience_persona="target audience",
                max_length=300
            )
            
            refinement_response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a caption optimization expert. Improve captions while maintaining brand voice."
                    },
                    {
                        "role": "user",
                        "content": refinement_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            refined_caption = refinement_response.choices[0].message.content.strip()
            
            return {
                "status": "success",
                "original_caption": original_caption,
                "refined_caption": refined_caption,
                "analysis": analysis,
                "previous_engagement_rate": engagement_metrics.get("engagement_rate", 0),
                "improvement_suggestions": analysis
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class SchedulingService:
    """Service for scheduling posts to social platforms"""
    
    # Best times to post per platform (UTC)
    OPTIMAL_POSTING_TIMES = {
        Platform.INSTAGRAM: [11, 13, 19],  # 11am, 1pm, 7pm
        Platform.LINKEDIN: [8, 12, 17],    # 8am, 12pm, 5pm
        Platform.TWITTER: [9, 14, 17],     # 9am, 2pm, 5pm
        Platform.FACEBOOK: [13, 19],       # 1pm, 7pm
        Platform.TIKTOK: [6, 10, 18],      # 6am, 10am, 6pm
    }
    
    def get_optimal_posting_time(self, platform: Platform) -> datetime:
        """Calculate optimal posting time for platform"""
        now = datetime.utcnow()
        
        optimal_hours = self.OPTIMAL_POSTING_TIMES.get(platform, [12])
        current_hour = now.hour
        
        # Find next optimal hour
        for hour in optimal_hours:
            if hour > current_hour:
                return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # If past all today's times, schedule for tomorrow
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
    
    async def schedule_post(
        self,
        platform: Platform,
        caption: str,
        hashtags: List[str],
        scheduled_time: datetime = None,
        image_url: str = None,
        video_url: str = None
    ) -> Dict:
        """Schedule post for publishing (mock implementation)"""
        
        if not scheduled_time:
            scheduled_time = self.get_optimal_posting_time(platform)
        
        post_data = {
            "platform": platform.value,
            "caption": caption,
            "hashtags": hashtags,
            "scheduled_time": scheduled_time.isoformat(),
            "image_url": image_url,
            "video_url": video_url,
            "status": "scheduled",
            "scheduled_at": datetime.utcnow().isoformat()
        }
        
        # In production, integrate with platform APIs:
        # - Meta (Facebook/Instagram) Graph API
        # - LinkedIn REST API
        # - Twitter/X API v2
        # - TikTok Business API
        
        return {
            "status": "success",
            "scheduled_post": post_data,
            "message": f"Post scheduled for {scheduled_time}"
        }


class PromptOptimizationService:
    """Service for continuous prompt optimization based on feedback"""
    
    def __init__(self):
        self.history = []
    
    def track_performance(self, post_id: str, metrics: Dict):
        """Track post performance for learning"""
        self.history.append({
            "post_id": post_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_performance_patterns(self, platform: Platform) -> Dict:
        """Analyze what works best for this platform"""
        platform_history = [h for h in self.history if h.get("platform") == platform.value]
        
        if not platform_history:
            return {"status": "insufficient_data"}
        
        avg_engagement = sum(h["metrics"].get("engagement_rate", 0) for h in platform_history) / len(platform_history)
        
        return {
            "platform": platform.value,
            "avg_engagement_rate": avg_engagement,
            "total_posts": len(platform_history),
            "best_performing": max(platform_history, key=lambda x: x["metrics"].get("engagement_rate", 0)),
            "patterns": "Performance patterns identified"
        }
    
    async def auto_refine_template(
        self,
        platform: Platform,
        brand_keywords: List[str],
        tone: str
    ) -> Dict:
        """Automatically refine templates based on historical performance"""
        
        patterns = self.get_performance_patterns(platform)
        
        if patterns.get("status") == "insufficient_data":
            return {"status": "waiting_for_data", "message": "Need more data to optimize"}
        
        return {
            "status": "optimized",
            "platform": platform.value,
            "insights": patterns,
            "recommendation": "Continue with current strategy or test variations"
        }
