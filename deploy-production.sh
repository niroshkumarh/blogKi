#!/bin/bash
# Production Deployment Script for Wide Angle Blog
# Run this on your production server after pulling latest code

set -e  # Exit on error

echo "🚀 Wide Angle Blog - Production Deployment"
echo "==========================================="

# Step 1: Pull latest code
echo ""
echo "📥 Pulling latest code from Git..."
git pull origin docker-deployment

# Step 2: Check/Update .env file
echo ""
echo "🔍 Checking environment configuration..."
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env from env.docker.example"
    exit 1
fi

# Verify critical environment variables
if ! grep -q "FLASK_ENV=production" .env; then
    echo "⚠️  Adding FLASK_ENV=production to .env..."
    echo "FLASK_ENV=production" >> .env
fi

if ! grep -q "PREFERRED_URL_SCHEME=https" .env; then
    echo "⚠️  Adding PREFERRED_URL_SCHEME=https to .env..."
    echo "PREFERRED_URL_SCHEME=https" >> .env
fi

# Check redirect URI
CURRENT_REDIRECT=$(grep REDIRECT_URI .env | cut -d'=' -f2)
echo "Current REDIRECT_URI: $CURRENT_REDIRECT"
if [[ ! "$CURRENT_REDIRECT" =~ ^https:// ]]; then
    echo "⚠️  WARNING: REDIRECT_URI should use HTTPS for production!"
    echo "   Expected: https://blogs.iqubekct.ac.in/auth/callback"
fi

# Step 3: Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down

# Step 4: Rebuild images
echo ""
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Step 5: Start containers
echo ""
echo "▶️  Starting containers..."
docker-compose up -d

# Step 6: Wait for database
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

# Step 7: Initialize database
echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T web python init_db_postgres.py

# Step 8: Check status
echo ""
echo "✅ Checking container status..."
docker-compose ps

# Step 9: Test endpoint
echo ""
echo "🧪 Testing application..."
sleep 5
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4343/test)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Application is responding (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Application returned HTTP $HTTP_STATUS"
fi

# Step 10: Show logs
echo ""
echo "📋 Recent logs:"
docker-compose logs --tail=20 web

echo ""
echo "==========================================="
echo "✅ Deployment complete!"
echo ""
echo "📊 Next steps:"
echo "   1. Test login at: https://blogs.iqubekct.ac.in/"
echo "   2. Monitor logs: docker-compose logs -f web"
echo "   3. Check status: docker-compose ps"
echo ""
echo "🔧 Troubleshooting:"
echo "   • View logs: docker logs blogki-web"
echo "   • Restart: docker-compose restart web"
echo "   • Rebuild: docker-compose up -d --build web"
echo "==========================================="

