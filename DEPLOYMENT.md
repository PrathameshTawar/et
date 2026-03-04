# SatyaSetu Deployment Guide

Complete guide for deploying SatyaSetu in different environments.

## 🚀 Quick Start

### Development Setup (Windows)
```powershell
# Run the setup script
.\scripts\setup.ps1

# Start all services
.\start-all.bat
```

### Development Setup (Linux/Mac)
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys

# Frontend setup
cd ../frontend
npm install
cp .env.local.example .env.local

# Start services
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend && npm run dev
```

### Docker Deployment
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit the .env files with your configuration

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Configuration

### Backend Environment Variables (.env)
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# External Services (Required for production)
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_env_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Database & Cache
REDIS_URL=redis://localhost:6379

# Security
RATE_LIMIT_PER_MINUTE=60
MAX_AUDIO_SIZE_MB=10
```

### Frontend Environment Variables (.env.local)
```bash
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE_RECORDING=true
NEXT_PUBLIC_DEBUG_MODE=false
```

## 🏗️ Production Deployment

### Prerequisites
- Docker & Docker Compose
- SSL certificates (for HTTPS)
- Domain name
- External services configured (OpenAI, Pinecone, etc.)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Application Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd satyasetu

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit configuration files
nano backend/.env
nano frontend/.env.local

# Deploy with production profile
docker-compose --profile production up -d
```

### Step 3: SSL & Reverse Proxy (Nginx)
```bash
# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Nginx configuration is included in docker-compose.yml
```

## 🔍 Monitoring & Maintenance

### Health Checks
```bash
# Check service health
curl http://localhost:8000/
curl http://localhost:8000/api/voice/health
curl http://localhost:3000/

# Check Docker services
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
```

### Monitoring Endpoints
- **System Health**: `GET /api/admin/stats`
- **Pipeline Status**: `GET /api/admin/pipeline-status`
- **Metrics**: `GET /api/admin/events`

### Log Management
```bash
# View logs
docker-compose logs -f

# Log rotation (add to crontab)
0 2 * * * docker system prune -f
```

## 🔄 Updates & Rollbacks

### Update Deployment
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
./scripts/deploy.sh production
```

### Rollback
```bash
# Stop current deployment
docker-compose down

# Load backup images
docker load < backups/20240101_120000/backend.tar
docker load < backups/20240101_120000/frontend.tar

# Start with backup
docker-compose up -d
```

## 🛡️ Security Considerations

### Production Security Checklist
- [ ] Change default passwords
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set secure environment variables
- [ ] Enable logging and monitoring
- [ ] Regular security updates

### Network Security
```bash
# Firewall rules (UFW)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📊 Performance Optimization

### Backend Optimization
- Use Redis for caching
- Configure connection pooling
- Enable gzip compression
- Set appropriate worker processes

### Frontend Optimization
- Enable Next.js optimization
- Configure CDN for static assets
- Implement proper caching headers
- Use image optimization

### Database Optimization
- Configure Redis persistence
- Set up Redis clustering (if needed)
- Monitor memory usage
- Regular backups

## 🚨 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common fixes
- Check .env file configuration
- Verify API keys are valid
- Ensure Redis is running
- Check port conflicts
```

#### Frontend build fails
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### WebSocket connection fails
```bash
# Check CORS configuration
# Verify WebSocket URL in frontend
# Check firewall/proxy settings
```

### Performance Issues
- Monitor CPU/memory usage
- Check Redis memory usage
- Review API response times
- Analyze error rates

## 📞 Support

### Getting Help
1. Check logs first: `docker-compose logs`
2. Review configuration files
3. Check GitHub issues
4. Contact support team

### Useful Commands
```bash
# Restart services
docker-compose restart

# Update single service
docker-compose up -d --no-deps backend

# Scale services
docker-compose up -d --scale backend=2

# Database backup
docker-compose exec redis redis-cli BGSAVE
```