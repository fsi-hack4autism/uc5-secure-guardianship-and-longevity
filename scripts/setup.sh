#!/bin/bash
# Setup development environment

echo "🚀 Setting up AI Financial Guardrails Development Environment..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update if needed."
fi

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is ready
echo "🔍 Checking API health..."
curl -f http://localhost:8000/health || {
    echo "❌ API health check failed"
    docker-compose logs api-gateway
    exit 1
}

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Services are running:"
echo "   - API Gateway: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📚 Useful commands:"
echo "   - docker-compose logs -f         # View logs"
echo "   - docker-compose ps              # Check status"
echo "   - docker-compose down            # Stop services"
echo "   - docker-compose up -d           # Start services"
echo ""
