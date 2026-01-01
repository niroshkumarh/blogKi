#!/bin/bash

# Wide Angle Blog - Docker Quick Start Script

echo "🐳 Wide Angle Blog - Docker Setup"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Creating .env from example..."
    cp env.docker.example .env
    echo ""
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and update:"
    echo "   - CLIENT_SECRET (from Azure Portal)"
    echo "   - ADMIN_EMAILS (your email address)"
    echo "   - SECRET_KEY (random string)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Found .env file"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start containers
echo "🏗️  Building and starting containers..."
echo ""

docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Containers started successfully!"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
    echo ""
    echo "🎉 Your blog is ready!"
    echo ""
    echo "   🌐 Blog: http://localhost:4343"
    echo "   📊 Database: localhost:5432"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop containers:"
    echo "   docker-compose stop"
    echo ""
else
    echo ""
    echo "❌ Failed to start containers"
    echo "   Check the logs: docker-compose logs"
    exit 1
fi

