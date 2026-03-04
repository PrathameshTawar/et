"""
LLM Prompt Templates for Content Generation
Module A: Automated Social Media Content Engine
"""

# Platform-specific prompt templates
PLATFORM_TEMPLATES = {
    "instagram": {
        "caption_format": """Create an Instagram caption for a {brand_name} post about {topic}.
        
Brand Identity:
- Keywords: {keywords}
- Tone: {tone}
- Audience: {audience_persona}

Requirements:
- 150-300 characters (Instagram optimal)
- Emoji-rich, casual, engaging
- End with a call-to-action ({cta})
- Include relevant hashtags (3-5 max)
- Make it shareable and relatable

Generate ONLY the caption text, no explanations.""",
        
        "hashtags": """Generate 5-8 relevant hashtags for an Instagram post about {topic} for {brand_name}.
Return ONLY hashtags (each on a new line, starting with #).
Focus on: {keywords}""",
        
        "cta": """Create a compelling call-to-action for Instagram about {topic}.
Keep it under 10 words. Be playful and engaging.
Brand tone: {tone}"""
    },
    
    "linkedin": {
        "caption_format": """Create a LinkedIn post for {brand_name} about {topic}.

Brand Identity:
- Keywords: {keywords}
- Tone: {tone} (professional, insightful)
- Audience: {audience_persona}

Requirements:
- Professional, thought-leadership focused
- 200-400 characters
- Include a hook in the first 1-2 lines
- Add industry insights
- End with engagement question or CTA
- Minimal emojis (max 1-2)

Generate ONLY the post text, no explanations.""",
        
        "hashtags": """Generate 3-5 professional LinkedIn hashtags for {topic}.
Return ONLY hashtags (each on a new line, starting with #).
Focus on industry and expertise: {keywords}""",
        
        "cta": """Create a professional call-to-action for LinkedIn about {topic}.
Keep it under 15 words. Encourage discussion or learning.
Brand focus: {keywords}"""
    },
    
    "twitter": {
        "caption_format": """Create a Twitter/X post for {brand_name} about {topic}.

Brand Identity:
- Keywords: {keywords}
- Tone: {tone}
- Audience: {audience_persona}

Requirements:
- Under 280 characters (Twitter limit)
- Concise, punchy, engaging
- Include 1-2 relevant hashtags
- Optional trend/hook reference
- Clear CTA or conversation starter

Generate ONLY the tweet text, no explanations.""",
        
        "hashtags": """Generate 1-2 trending-aware hashtags for {topic} on Twitter.
Return ONLY hashtags (each on a new line, starting with #).
Keep relevant to: {keywords}""",
        
        "cta": """Create a concise call-to-action for Twitter about {topic}.
Under 10 words. Be witty or trending-aware.
Tone: {tone}"""
    }
}

# Content generation prompt template (for multi-platform)
CONTENT_BRIEF_TEMPLATE = """You are a social media content strategist for {brand_name}.

Brand Profile:
- Keywords: {keywords}
- Tone: {tone}
- Audience Persona: {audience_persona}
- Primary Platforms: {platforms}
- Campaign Goal: {campaign_goal}

Create a content brief for a post about "{topic}" that will:
1. Resonate with the audience
2. Align with brand voice
3. Drive engagement
4. Include platform-specific recommendations

Format your response as:
HOOK: [Opening line to grab attention]
BODY: [Main message - 2-3 sentences]
CTA: [Call-to-action]
HASHTAGS: [3-5 relevant hashtags]
BEST PLATFORMS: [Which platforms work best]
OPTIMAL TIME: [Best time to post]

Be creative, authentic, and data-driven."""

# Feedback-driven prompt optimization template
PROMPT_OPTIMIZATION_TEMPLATE = """Analyze the following social media content performance:

Post Content: {post_content}
Platform: {platform}
Metrics:
- Likes: {likes}
- Comments: {comments}
- Shares: {shares}
- CTR: {ctr}%
- Overall Engagement Rate: {engagement_rate}%

Brand Profile:
- Keywords: {keywords}
- Tone: {tone}

Based on this performance, recommend:
1. What worked well (be specific)
2. What underperformed
3. Specific improvements for next post
4. Recommended angle/topic for next content
5. Optimal posting time for this platform

Keep tone: {tone}
Focus on: {keywords}"""

# Image generation prompt template
IMAGE_GENERATION_TEMPLATE = """Generate a description for an AI image for {brand_name}.

Content Context:
- Topic: {topic}
- Platform: {platform}
- Audience: {audience_persona}

Brand Guidelines:
- Keywords: {keywords}
- Brand Colors: {brand_colors}
- Visual Style: {visual_style}
- Tone: {tone}

Create a detailed image prompt (under 200 words) for Dall-E/Midjourney that includes:
- Scene composition
- Color palette and mood
- Typography (if any)
- Visual elements that reinforce brand identity
- High-quality, professional feel

Start with: "A professional {platform}-optimized image that..."
Make it specific and visually descriptive."""

# Video generation prompt template
VIDEO_GENERATION_TEMPLATE = """Create a video script for {brand_name}'s {platform} video.

Content:
- Topic: {topic}
- Duration: {duration} seconds
- Audience: {audience_persona}

Brand Profile:
- Keywords: {keywords}
- Tone: {tone}
- Visual Style: {visual_style}

Script Format:
[00-05s] HOOK: [Grab attention in first 5 seconds]
[05-15s] BODY: [Main message and benefits]
[15-20s] CALL-TO-ACTION: [Clear CTA]

Requirements:
- Fast-paced, dynamic transitions
- Text overlays for key points (6-8 words max)
- Trending audio/music style: {music_style}
- Emoji/graphics recommendations
- Platform-specific dimensions: {platform}

Make it viral-worthy and on-brand."""

# Caption optimization after engagement feedback
CAPTION_REFINEMENT_TEMPLATE = """Your previous caption got {engagement_rate}% engagement.

Original Caption: {original_caption}
Performance: {performance_analysis}

Refine this caption to improve performance while maintaining brand voice: {tone}

Consider:
1. Hook strength (first 5 words critical)
2. Emotional appeal vs. rational
3. CTA clarity
4. Hashtag placement and selection
5. Emoji usage

New Caption Requirements:
- Same topic: {topic}
- Platform: {platform}
- Target audience: {audience_persona}
- Max length: {max_length} characters

Provide the refined caption only."""

# Hashtag generation with trend awareness
HASHTAG_STRATEGY_TEMPLATE = """Generate a hashtag strategy for {brand_name}.

Campaign: {topic}
Platform: {platform}
Audience: {audience_persona}
Keywords: {keywords}

Create three tiers of hashtags:

TIER 1 - BRAND HASHTAGS (2-3):
[Your unique branded hashtags]
[Community-building hashtags]

TIER 2 - TRENDING HASHTAGS (3-4):
[Trending in {audience_persona}]
[Current events/trends relevant to {keywords}]

TIER 3 - LONG-TAIL HASHTAGS (2-3):
[Niche, specific hashtags]
[Low competition, high relevance]

For Platform: {platform}
Optimal hashtag count: {optimal_hashtag_count}

Format each as: #hashtag"""

# Multi-platform content adaptation
MULTI_PLATFORM_TEMPLATE = """Adapt the following content for multiple platforms.

Original Post:
{original_content}

Brand: {brand_name}
Tone: {tone}
Keywords: {keywords}

Adapt this message for:
1. INSTAGRAM
   - Caption (150-300 chars)
   - Hashtags (5-8)
   - CTA

2. LINKEDIN
   - Post (200-400 chars)
   - Hashtags (3-5)
   - CTA

3. TWITTER/X
   - Tweet (under 280 chars)
   - Hashtags (1-2)
   - CTA

Each must:
- Maintain core message
- Follow platform best practices
- Match brand voice
- Include platform-specific emojis/formatting
- Drive engagement for that audience

Return as structured JSON."""
