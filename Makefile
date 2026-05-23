.PHONY: help setup build up down logs test clean db-migrate

help:
	@echo "📚 Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make setup          - Set up development environment"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View container logs"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run tests"
	@echo "  make test-api       - Test API endpoints"
	@echo "  make lint           - Run linters"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-seed        - Seed test data"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean up containers and files"
	@echo "  make clean-all      - Deep clean (remove volumes)"
	@echo ""

setup:
	@echo "🚀 Setting up development environment..."
	@cp .env.example .env || true
	@echo "✅ .env file ready"
	@echo ""
	@echo "📦 Installing backend dependencies..."
	@pip install -r backend/api-gateway/requirements.txt || echo "Install manually if needed"
	@echo ""
	@echo "✅ Setup complete! Run 'make up' to start"

build:
	@echo "🐳 Building Docker images..."
	docker-compose build

up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo ""
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo ""
	@echo "✅ Services running:"
	@echo "   - API: http://localhost:8000"
	@echo "   - Docs: http://localhost:8000/docs"
	@echo "   - Frontend: http://localhost:3000"

down:
	@echo "⛔ Stopping services..."
	docker-compose down

logs:
	@docker-compose logs -f

test:
	@echo "🧪 Running tests..."
	@docker-compose exec api-gateway pytest tests/

test-api:
	@echo "🧪 Testing API endpoints..."
	@curl -X GET http://localhost:8000/health || echo "API not ready"

lint:
	@echo "🔍 Running linters..."
	@docker-compose exec api-gateway flake8 src/

db-migrate:
	@echo "🗄️  Running database migrations..."
	@docker-compose exec api-gateway python -m alembic upgrade head

db-seed:
	@echo "🌱 Seeding database with test data..."
	@echo "Add seed script here"

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down --remove-orphans
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-all: clean
	@echo "🧹 Deep clean..."
	docker-compose down -v
	@echo "✅ All containers and volumes removed"

install-deps:
	@echo "📦 Installing dependencies..."
	pip install -r backend/api-gateway/requirements.txt
	cd frontend/guardian-dashboard && npm install

health-check:
	@echo "🏥 Health check..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not responding"
	@docker-compose ps
