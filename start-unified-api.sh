#!/bin/bash

# Unified Legal AI API Quick Start Script

set -e

echo "🚀 Starting Unified Legal AI API..."

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your-key'"
    exit 1
fi

# Create .env file for unified API if it doesn't exist
if [ ! -f "unified-api/.env" ]; then
    echo "📝 Creating unified-api/.env from example..."
    cp unified-api/.env.example unified-api/.env
    
    # Update the .env file with the OPENAI_API_KEY
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/OPENAI_API_KEY=\"your-openai-api-key\"/OPENAI_API_KEY=\"$OPENAI_API_KEY\"/g" unified-api/.env
    else
        # Linux
        sed -i "s/OPENAI_API_KEY=\"your-openai-api-key\"/OPENAI_API_KEY=\"$OPENAI_API_KEY\"/g" unified-api/.env
    fi
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    echo "Please install Docker and docker-compose first"
    exit 1
fi

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.unified.yml down

# Build and start services
echo "🔨 Building services..."
docker-compose -f docker-compose.unified.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.unified.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Unified API is healthy!"
else
    echo "⚠️  Unified API health check failed, checking logs..."
    docker-compose -f docker-compose.unified.yml logs unified-api | tail -20
fi

# Display access information
echo ""
echo "🎉 Unified Legal AI API is running!"
echo ""
echo "📚 Access points:"
echo "  - API Documentation: http://localhost/docs"
echo "  - Alternative docs: http://localhost/redoc"
echo "  - API Gateway: http://localhost/api/v1/"
echo "  - Neo4j Browser: http://localhost:7474"
echo "  - Direct API: http://localhost:8080"
echo ""
echo "🔑 Authentication:"
echo "  - Use 'Authorization: Bearer sk_unified_test' header for testing"
echo "  - Or use your Unstract API key if available"
echo ""
echo "💡 Quick test:"
echo "  curl -X GET http://localhost:8080/health"
echo ""
echo "📋 View logs:"
echo "  docker-compose -f docker-compose.unified.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose -f docker-compose.unified.yml down"