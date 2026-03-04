"""
Database Models for AI Media Platform
Uses SQLAlchemy ORM for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

# Association tables for many-to-many relationships
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('tag', String)
)

# ============ USERS & AUTHENTICATION ============
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brands = relationship("Brand", back_populates="owner", cascade="all, delete-orphan")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    behaviors = relationship("UserBehavior", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


# ============ BRAND & CONTENT GENERATION (MODULE A) ============
class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    owner_id = Column(String, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    keywords = Column(JSON)  # ["fitness", "wellness"]
    tone = Column(String)  # "professional", "playful", "luxury"
    audience_persona = Column(JSON)  # {"age": "25-35", "interests": ["yoga"]}
    platforms = Column(JSON)  # ["instagram", "linkedin", "twitter"]
    brand_colors = Column(JSON)  # ["#FF5733", "#33FF57"]
    brand_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="brands")
    generated_posts = relationship("GeneratedPost", back_populates="brand", cascade="all, delete-orphan")
    scheduled_posts = relationship("ScheduledPost", back_populates="brand", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Brand {self.name}>"


class GeneratedPost(Base):
    __tablename__ = "generated_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    brand_id = Column(String, ForeignKey('brands.id'), nullable=False)
    platform = Column(String)  # "instagram", "linkedin", "twitter"
    caption = Column(Text, nullable=False)
    hashtags = Column(JSON)  # ["#fitness", "#wellness"]
    cta = Column(String)  # Call-to-action
    image_url = Column(String)  # URL to generated image
    video_url = Column(String)  # URL to generated video
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="generated_posts")
    engagement = relationship("EngagementMetric", back_populates="post", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GeneratedPost {self.id[:8]}>"


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    brand_id = Column(String, ForeignKey('brands.id'), nullable=False)
    post_id = Column(String, ForeignKey('generated_posts.id'))
    platform = Column(String)
    scheduled_time = Column(DateTime)
    published_time = Column(DateTime)
    status = Column(String, default="scheduled")  # "scheduled", "published", "failed"
    external_post_id = Column(String)  # ID from social platform
    
    # Relationships
    brand = relationship("Brand", back_populates="scheduled_posts")
    
    def __repr__(self):
        return f"<ScheduledPost {self.status}>"


class EngagementMetric(Base):
    __tablename__ = "engagement_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    post_id = Column(String, ForeignKey('generated_posts.id'), unique=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    watch_time_seconds = Column(Float, default=0)
    ctr = Column(Float)  # Click-through rate
    engagement_rate = Column(Float)
    sentiment = Column(String)  # "positive", "neutral", "negative"
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("GeneratedPost", back_populates="engagement")
    
    def __repr__(self):
        return f"<EngagementMetric {self.id[:8]}>"


# ============ NEWS & PERSONALIZED FEED (MODULE B) ============
class Article(Base):
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    source = Column(String)
    source_url = Column(String)
    category = Column(String)
    author = Column(String)
    published_date = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
    embedding = relationship("ArticleEmbedding", back_populates="article", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article {self.title[:30]}>"


class ArticleTag(Base):
    __tablename__ = "article_tags"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    article_id = Column(String, ForeignKey('articles.id'), nullable=False)
    tag = Column(String, nullable=False)  # Topic, entity, keyword
    tag_type = Column(String)  # "topic", "entity", "sentiment"
    confidence = Column(Float)  # 0-1, confidence score
    
    # Relationships
    article = relationship("Article", back_populates="tags")
    
    def __repr__(self):
        return f"<ArticleTag {self.tag}>"


class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    article_id = Column(String, ForeignKey('articles.id'), unique=True, nullable=False)
    embedding = Column(JSON)  # Vector embedding (1536-dim for OpenAI)
    model = Column(String)  # "text-embedding-ada-002"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="embedding")
    
    def __repr__(self):
        return f"<ArticleEmbedding {self.id[:8]}>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey('users.id'), unique=True, nullable=False)
    interests = Column(JSON, default=[])  # ["tech", "science", "politics"]
    interests_embedding = Column(JSON)  # Vector representation of interests
    read_time_avg = Column(Float)  # Average read time in seconds
    engagement_preference = Column(String)  # "high", "medium", "low"
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_profile")
    
    def __repr__(self):
        return f"<UserProfile {self.user_id[:8]}>"


class UserBehavior(Base):
    __tablename__ = "user_behavior"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    article_id = Column(String, ForeignKey('articles.id'), nullable=False)
    action = Column(String)  # "click", "read", "like", "share", "skip"
    read_time_seconds = Column(Integer, default=0)
    scroll_depth = Column(Float)  # 0-1, how far down article
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="behaviors")
    
    def __repr__(self):
        return f"<UserBehavior {self.action}>"


# ============ VIDEO EDITING (MODULE C) ============
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String)
    duration_seconds = Column(Float)
    resolution = Column(String)  # "1920x1080"
    fps = Column(Float)
    size_bytes = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scenes = relationship("Scene", back_populates="video", cascade="all, delete-orphan")
    captions = relationship("Caption", back_populates="video", cascade="all, delete-orphan")
    thumbnails = relationship("Thumbnail", back_populates="video", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Video {self.filename}>"


class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    start_time = Column(Float)  # Seconds
    end_time = Column(Float)  # Seconds
    scene_type = Column(String)  # "cut", "fade", "silence"
    importance_score = Column(Float)  # 0-1, how important/engaging
    description = Column(String)
    
    # Relationships
    video = relationship("Video", back_populates="scenes")
    
    def __repr__(self):
        return f"<Scene {self.scene_type}>"


class Caption(Base):
    __tablename__ = "captions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    start_time = Column(Float)  # Seconds
    end_time = Column(Float)
    text = Column(String, nullable=False)
    confidence = Column(Float)  # 0-1, speech-to-text confidence
    language = Column(String, default="en")
    
    # Relationships
    video = relationship("Video", back_populates="captions")
    
    def __repr__(self):
        return f"<Caption {self.text[:30]}>"


class Thumbnail(Base):
    __tablename__ = "thumbnails"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    frame_time = Column(Float)  # Seconds, where thumbnail extracted
    image_path = Column(String)
    image_url = Column(String)
    has_text_overlay = Column(Boolean, default=False)
    has_face = Column(Boolean, default=False)
    ctr_potential = Column(Float)  # 0-1, predicted CTR based on image
    
    # Relationships
    video = relationship("Video", back_populates="thumbnails")
    
    def __repr__(self):
        return f"<Thumbnail {self.id[:8]}>"


class Export(Base):
    __tablename__ = "exports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    platform = Column(String)  # "instagram", "youtube", "tiktok"
    format = Column(String)  # "mp4", "webm"
    resolution = Column(String)  # "1080x1920"
    file_size_bytes = Column(Integer)
    export_path = Column(String)
    export_url = Column(String)
    status = Column(String, default="pending")  # "pending", "processing", "completed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    video = relationship("Video", back_populates="exports")
    
    def __repr__(self):
        return f"<Export {self.platform}>"
