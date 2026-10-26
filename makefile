# Define standard variables to keep commands clean and easy to update
export NODE_OPTIONS := --max-old-space-size=2048
DOCKER_COMPOSE := docker compose -f docker-compose-local.yml

.PHONY: dev dev-all docker-up docker-up-d docker-down docker-rebuild mcp-test mcp-watch

# Start only the web development environment
dev:
	pnpm --filter web --filter admin dev
    
# Fast startup (reuses existing built images instantly)
docker-up:
	$(DOCKER_COMPOSE) up

# Background startup (daemon mode) so you can run tests in parallel
docker-up-d:
	$(DOCKER_COMPOSE) up -d

# Stop the main stack
docker-down:
	$(DOCKER_COMPOSE) down

# Use this ONLY when you change code and need a fresh build
docker-rebuild:
	$(DOCKER_COMPOSE) up --build

mcp-test:
	cd apps/mcp_server && \
	uv pip install -r requirements.txt && \
	OPENAPI_DOCS_URL=http://localhost:8000/api/schema/?format=json \
	PLANE_API_URL=http://localhost:8000/api/v1 \
	uv run pytest

COMPOSE_FILE = docker-compose-mcp-test.yml

mcp-integration-test:
	@echo "🚀 Starting test environment..."
	docker compose -f docker-compose-mcp-test.yml up \
		--build \
		--abort-on-container-exit \
		--exit-code-from mcp-tests
	
	@echo "✅ Finished MCP test suite"