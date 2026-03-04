#!/bin/bash

# SatyaSetu Production Deployment Script
set -e

echo "🚀 Starting SatyaSetu deployment..."

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

echo "📋 Environment: $ENVIRONMENT"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to check if service is running
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null; then
            echo "✅ $service is healthy"
            return 0
        fi
        
        echo "⏳ Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to start"
    return 1
}

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Check environment files
if [ ! -f "backend/.env" ]; then
    echo "❌ Backend .env file not found"
    echo "📝 Please copy backend/.env.example to backend/.env and configure it"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Frontend .env.local file not found"
    echo "📝 Please copy frontend/.env.local.example to frontend/.env.local and configure it"
    exit 1
fi

# Backup current deployment (if exists)
if docker-compose ps | grep -q "Up"; then
    echo "💾 Creating backup of current deployment..."
    
    # Backup database/redis data
    docker-compose exec -T redis redis-cli BGSAVE || true
    
    # Export current images
    docker save satyasetu-backend:latest > "$BACKUP_DIR/backend.tar" 2>/dev/null || true
    docker save satyasetu-frontend:latest > "$BACKUP_DIR/frontend.tar" 2>/dev/null || true
    
    echo "✅ Backup created in $BACKUP_DIR"
fi

# Build new images
echo "🔨 Building application images..."
docker-compose build --no-cache

# Run tests
echo "🧪 Running tests..."
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
test_exit_code=$?

if [ $test_exit_code -ne 0 ]; then
    echo "❌ Tests failed, aborting deployment"
    exit 1
fi

echo "✅ All tests passed"

# Stop current services
echo "🛑 Stopping current services..."
docker-compose down

# Start new services
echo "🚀 Starting new services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
check_service "Backend API" "http://localhost:8000/"
check_service "Frontend" "http://localhost:3000/"

# Run smoke tests
echo "🧪 Running smoke tests..."

# Test API endpoints
curl -f http://localhost:8000/api/voice/health || {
    echo "❌ Voice API health check failed"
    exit 1
}

curl -f http://localhost:8000/api/admin/stats || {
    echo "❌ Admin API health check failed"
    exit 1
}

# Test frontend
curl -f http://localhost:3000/ || {
    echo "❌ Frontend health check failed"
    exit 1
}

echo "✅ All smoke tests passed"

# Show deployment status
echo "📊 Deployment Status:"
docker-compose ps

# Show logs
echo "📝 Recent logs:"
docker-compose logs --tail=20

echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Monitoring:"
echo "   Health: http://localhost:8000/api/admin/stats"
echo "   Logs: docker-compose logs -f"
echo ""
echo "🔧 Management:"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Update: ./scripts/deploy.sh"