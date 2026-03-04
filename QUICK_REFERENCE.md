# 📚 Quick Reference Guide

## 🎯 What You Have

An **enterprise-grade AI-powered media platform** with 3 fully-integrated modules:

```
🎬 AI MEDIA PLATFORM
│
├─ 📱 SOCIAL MEDIA ENGINE (Module A)
│  └─ Generate → Schedule → Analyze → Optimize
│
├─ 📰 NEWS FEED (Module B)
│  └─ Ingest → Tag → Recommend → Personalize
│
└─ 🎥 VIDEO EDITOR (Module C)
   └─ Upload → Analyze → Edit → Export
```

---

## 🚀 Quick Start (5 minutes)

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=sk-your-key-here
uvicorn main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

### Open Browser
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Where Everything Is

### Backend Services (Core Logic)
```
backend/
├── models.py                    → Database structure
├── llm_templates.py             → AI prompts
├── services_social_engine.py    → Module A logic
├── services_news_feed.py        → Module B logic
├── services_video_editor.py     → Module C logic
└── api/routes/
    ├── social.py                → Module A APIs
    ├── feed.py                  → Module B APIs
    └── video.py                 → Module C APIs
```

### Frontend Pages (User Interface)
```
frontend/app/
├── page.tsx                     → Main dashboard
├── social/page.tsx              → Social engine UI
├── feed/page.tsx                → News feed UI
└── videos/page.tsx              → Video editor UI
```

---

## 🔌 API Quick Reference

### Social Media Engine
```
Generate Content:
POST /api/social/generate-content
  Input: brand_id, topic, platforms
  Output: captions, hashtags per platform

Schedule Post:
POST /api/social/schedule-post
  Input: platform, caption, hashtags, scheduled_time
  Output: scheduled_post confirmation

Track Engagement:
POST /api/social/track-engagement
  Input: post_id, likes, comments, shares, clicks
  Output: metrics, engagement_rate
```

### News Feed
```
Generate Feed:
POST /api/feed/generate
  Input: user_id, limit (20)
  Output: ranked articles with recommendation_score

Track Click:
POST /api/feed/track-click
  Input: user_id, article_id, action, read_time
  Output: behavior recorded

Get Trending:
GET /api/feed/trending?limit=10
  Output: top articles
```

### Video Editor
```
Upload Video:
POST /api/videos/upload
  Input: video file
  Output: video_id, upload_time

Analyze Video:
POST /api/videos/analyze
  Input: video_id
  Output: scenes, captions, thumbnails

Export Video:
POST /api/videos/export
  Input: video_id, platforms
  Output: export_id, status
```

---

## 💾 Database Schema at a Glance

### User & Brand (Module A)
```
users → user_profiles
users → brands → generated_posts → engagement_metrics
        brands → scheduled_posts
```

### Articles & Feed (Module B)
```
articles → article_tags
articles → article_embeddings
users → user_behavior → articles
user_profiles → interests
```

### Videos (Module C)
```
users → videos → scenes
        videos → captions
        videos → thumbnails
        videos → exports
```

---

## 🤖 AI Integration Points

### Module A: LLM Integration
```python
# Content Generation
model: gpt-4
templates: caption_format, hashtags, cta

# Prompt Optimization
input: performance metrics
output: refined prompts
```

### Module B: NLP Integration
```python
# Article Processing
embedding: text-embedding-ada-002 (1536-dim)
tagging: topic, entities, sentiment

# Recommendations
similarity: cosine distance
algorithm: hybrid (content + behavior)
```

### Module C: Vision Integration
```python
# Scene Detection (mockable)
input: video file
output: scenes, importance scores

# Caption Generation
model: Whisper (speech-to-text)
enhancement: LLM-based emoji/formatting
```

---

## 📊 Data Flow Summary

```
Module A: Brand → LLM → Content → Platform → Engagement → Feedback
                                                               ↑
Module B: Articles → NLP → Embeddings → Recommendations ← User Behavior
                                          ↓
Module C: Video → Analysis → Captions → Export → Performance Metrics
```

---

## 🔑 Key Features Checklist

### Module A ✅
- [x] Brand profile creation
- [x] Multi-platform caption generation
- [x] Hashtag optimization
- [x] Schedule posts with optimal times
- [x] Track engagement metrics
- [x] Automatic prompt refinement
- [x] Platform-specific analytics

### Module B ✅
- [x] Article ingestion with NLP
- [x] Semantic embeddings
- [x] User behavior tracking
- [x] Interest profile management
- [x] Hybrid recommendation engine
- [x] Real-time feed generation
- [x] Trending vs personalized balance

### Module C ✅
- [x] Video upload
- [x] Scene detection
- [x] Highlight identification
- [x] Speech-to-text captions
- [x] Caption enhancement
- [x] Thumbnail generation
- [x] Multi-platform export

---

## 🎬 Example Workflows

### Create & Post Content (Module A)
```
1. Create Brand
   POST /api/social/brands/create
   
2. Generate Content
   POST /api/social/generate-content
   
3. Review & Schedule
   POST /api/social/schedule-post
   
4. Track Performance
   POST /api/social/track-engagement
   
5. Optimize Next Post
   POST /api/social/optimize-content
```

### Get Personalized Feed (Module B)
```
1. User Clicks Article
   POST /api/feed/track-click
   
2. Profile Updated
   (Automatically)
   
3. Request Feed
   POST /api/feed/generate
   
4. Get Recommendations
   Ranked by recommendation_score
```

### Edit & Export Video (Module C)
```
1. Upload Video
   POST /api/videos/upload
   
2. Analyze
   POST /api/videos/analyze
   
3. Review Suggestions
   GET /api/videos/scenes/{video_id}
   
4. Export
   POST /api/videos/export
```

---

## 🛠️ Configuration

### Environment Variables
```bash
# Backend
OPENAI_API_KEY=sk-your-key
DATABASE_URL=postgresql://user:pass@localhost/ai_media
REDIS_URL=redis://localhost:6379
DEBUG=False
JWT_SECRET=your-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Database Setup (First Time)
```bash
# Create database
createdb ai_media

# Create tables (manual via SQLAlchemy migration)
# Or use Alembic: alembic upgrade head
```

---

## 📈 Scaling Checklist

### For Production
- [ ] Set up PostgreSQL (production instance)
- [ ] Configure Redis caching
- [ ] Set up S3 for file storage
- [ ] Create environment variables
- [ ] Enable HTTPS
- [ ] Set up monitoring (DataDog, New Relic)
- [ ] Configure logging (ELK stack)
- [ ] Set up backup strategy
- [ ] Enable rate limiting
- [ ] Implement authentication

### For Performance
- [ ] Add database indexing
- [ ] Implement query caching
- [ ] Set up CDN for videos
- [ ] Use async for long tasks
- [ ] Implement vector DB for embeddings
- [ ] Add message queue for background jobs
- [ ] Use connection pooling
- [ ] Optimize frontend bundle size

---

## 🧪 Testing the System

### Test Social Engine
```bash
curl -X POST http://localhost:8000/api/social/generate-content \
  -H "Content-Type: application/json" \
  -d '{"brand_id":"test","topic":"AI launch","platforms":["instagram"]}'
```

### Test News Feed
```bash
curl http://localhost:8000/api/feed?user_id=test&limit=5
```

### Test Video Editor
```bash
curl -X POST http://localhost:8000/api/videos/upload \
  -F "file=@test_video.mp4"
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Platform overview |
| SETUP_GUIDE.md | Installation & running |
| ARCHITECTURE.md | System design |
| IMPLEMENTATION_SUMMARY.md | What was built |
| This File | Quick reference |

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
lsof -i :8000

# Install all dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version  # Should be 3.9+
```

### Frontend won't compile
```bash
# Clear node modules and reinstall
rm -rf node_modules
npm install

# Check Node version
node --version  # Should be 18+
```

### API calls fail
```bash
# Check backend is running
curl http://localhost:8000/docs

# Check CORS enabled
# Check environment variables set

# Check database connection
# Database URL correct in .env
```

### Database issues
```bash
# Check PostgreSQL running
psql -l

# Check database exists
createdb ai_media

# Check tables created
psql -c "\dt"
```

---

## 🎓 Learning Path

### Understanding the System
1. Read README.md (product overview)
2. Read ARCHITECTURE.md (system design)
3. Review models.py (database structure)
4. Review API routes (endpoint logic)
5. Review frontend pages (UI implementation)

### Running the System
1. Set up backend
2. Set up frontend
3. Test main dashboard
4. Test each module
5. Try API endpoints

### Extending the System
1. Modify LLM templates
2. Add new endpoints
3. Enhance UI components
4. Add database fields
5. Integrate real services (social APIs)

---

## 💡 Tips & Tricks

### Development
- Use `--reload` flag in uvicorn for hot reload
- Use `npm run dev` for Next.js hot reload
- Check http://localhost:8000/docs for API testing
- Use browser DevTools for frontend debugging

### API Testing
- Use curl, Postman, or Insomnia
- Test with mock data first
- Check response status codes
- Verify database records created

### Performance
- Use Redis for caching
- Enable database query logging
- Monitor OpenAI API usage
- Check frontend bundle size

---

## 📊 Metrics & KPIs

### Social Media Engine
- Content generation time: < 5s
- Engagement improvement: target 15-30%
- Optimization accuracy: > 85%

### News Feed
- Recommendation accuracy: > 75%
- Feed generation time: < 500ms
- User engagement: 3+ articles/session

### Video Editor
- Analysis time: < 2min per hour
- Export time: < 30min per hour
- User satisfaction: 4.5+/5

---

## 🎯 Next Actions

1. **Read SETUP_GUIDE.md** - Full installation details
2. **Start the system** - Backend + Frontend
3. **Access dashboard** - http://localhost:3000
4. **Test each module** - Try all three features
5. **Review code** - Understand the architecture
6. **Deploy** - Take to production
7. **Extend** - Add your own features

---

## 📞 File Locations Reference

```
Project Root
├── README.md                    ← Product overview
├── SETUP_GUIDE.md               ← Installation guide
├── ARCHITECTURE.md              ← System design
├── IMPLEMENTATION_SUMMARY.md    ← What was built
├── QUICK_REFERENCE.md           ← This file
│
├── backend/
│   ├── models.py                ← Database structure
│   ├── llm_templates.py          ← AI prompts
│   ├── services_*.py             ← Business logic
│   ├── api/routes/*.py           ← API endpoints
│   ├── main.py                   ← Entry point
│   └── requirements.txt           ← Dependencies
│
└── frontend/
    ├── app/page.tsx              ← Dashboard
    ├── app/*/page.tsx            ← Module pages
    ├── package.json              ← Dependencies
    └── ...
```

---

**Everything is ready to go! 🚀**

Start with SETUP_GUIDE.md for complete instructions.
