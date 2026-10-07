# Define standard variables to keep commands clean and easy to update
export NODE_OPTIONS := --max-old-space-size=2048
DOCKER_COMPOSE := docker compose -f docker-compose-local.yml

.PHONY: dev dev-all docker-up

# Start only the web development environment
dev:
	pnpm --filter web dev

# Start both web and admin development environments
dev-all:
	pnpm --filter web --filter admin dev

# Spin up local docker containers
docker-up:
	$(DOCKER_COMPOSE) up

