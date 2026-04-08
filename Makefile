.PHONY: help build up down restart logs shell clean health

# Default target
help:
	@echo "Weekly Report Streamlit App - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      - Build Docker image"
	@echo "  up         - Start container in background"
	@echo "  down       - Stop and remove container"
	@echo "  restart    - Restart container"
	@echo "  logs       - View container logs (follow)"
	@echo "  shell      - Open bash shell in container"
	@echo "  clean      - Remove container, images, and volumes"
	@echo "  health     - Check container health status"
	@echo "  dev        - Start in development mode (with logs)"
	@echo "  prod       - Start in production mode"
	@echo ""
	@echo "App will be available at: http://localhost:13333"

# Build Docker image
build:
	@echo "Building Docker image..."
	docker-compose build

# Start container in background
up:
	@echo "Starting container..."
	docker-compose up -d
	@echo "App is running at http://localhost:13333"

# Stop and remove container
down:
	@echo "Stopping container..."
	docker-compose down

# Restart container
restart:
	@echo "Restarting container..."
	docker-compose restart

# View logs (follow mode)
logs:
	docker-compose logs -f

# Open bash shell in container
shell:
	docker-compose exec streamlit-app bash

# Clean everything
clean:
	@echo "Cleaning up..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete"

# Check health status
health:
	@echo "Checking health status..."
	docker-compose ps
	@echo ""
	@curl -f http://localhost:13333/_stcore/health && echo "✅ App is healthy" || echo "❌ App is not responding"

# Development mode (with logs)
dev:
	@echo "Starting in development mode..."
	docker-compose up

# Production mode
prod:
	@echo "Starting in production mode..."
	docker-compose up -d --build
	@echo "App is running at http://localhost:13333"

# Rebuild and restart
rebuild:
	@echo "Rebuilding and restarting..."
	docker-compose up -d --build
	@echo "App is running at http://localhost:13333"
