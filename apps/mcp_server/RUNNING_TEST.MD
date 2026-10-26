# MCP Server Testing Documentation

This document outlines the architecture and execution guide for testing the Model Context Protocol (MCP) server extension in complete isolation, avoiding any modifications or clutter in the core Plane codebase.

---

## Architecture Overview

To ensure fast feedback loops and prevent upstream merge conflicts, the MCP server runs using its own dedicated Docker Compose setup (`docker-compose-mcp-test.yml`). The MCP test code is kept in `apps/mcp_server`, separate from Plane's core API code.

The setup provisions ephemeral dependencies alongside a lightweight background API instance to serve the OpenAPI schema required by the MCP server.

```
                   +-----------------------+
                   |       mcp-tests       |
                   |  (Runs pytest on MCP) |
                   +-----------+-----------+
                               |
                               | HTTP / Schema Fetch
                               v
                   +-----------------------+
                   |    test-api-server    |
                   | (Lightweight Django)  |
                   +-----------+-----------+
                               |
       +-----------------------+-----------------------+
       |                       |                       |
       v                       v                       v
+---------------+       +---------------+       +---------------+
|    test-db    |       |   test-redis  |       |   test-minio  |
| (PostgreSQL)  |       |   (Valkey)    |       |    (MinIO)    |
+---------------+       +---------------+       +---------------+
```

---

## Challenges & Solutions

### 1. OpenAPI Schema Dependency
* **Challenge:** The MCP server dynamically initializes its tool schema at startup by requesting the OpenAPI spec from `OPENAPI_DOCS_URL`. In-memory `pytest` executions do not expose a network-accessible HTTP server.
* **Solution:** Introduced a lightweight background `test-api-server` container using Django's built-in development server (`python manage.py runserver`). It shares the ephemeral test database and exposes `http://test-api-server:8000` on the test network.

### 2. Upstream Code Isolation
* **Challenge:** Nesting MCP into the main API test container caused Python import path issues and risked merge conflicts with upstream Plane updates.
* **Solution:** Decoupled the environment into a dedicated `docker-compose-mcp-test.yml` file. This keeps `apps/api` and `apps/mcp_server` as separate components while leaving Plane's core configuration untouched.

### 3. State Isolation & Execution Speed
* **Challenge:** Tests must be reliable and run quickly without leaving behind orphan data or requiring local disk cleanup.
* **Solution:** Applied `tmpfs` mounts across PostgreSQL, Valkey, RabbitMQ, and MinIO. Test data resides purely in RAM, providing high speed and guaranteed clean-slate teardowns.

---

## Usage Commands

### Prerequisites

- Run `./setup.sh` once to create `apps/api/.env` and the other environment files.
- Docker Compose must be installed and available as `docker compose`.
- The local API must already be running when using `make mcp-test`.

### Run Tests Against the Local API

Start the regular Plane stack, then run the MCP tests from the repository root:

```bash
make docker-up-d
make mcp-test
```

The `mcp-test` target installs the MCP requirements with `uv` and runs `pytest` against `http://localhost:8000`.

### Run Isolated Integration Tests

Build and launch the isolated API test environment. It automatically stops after the MCP test container exits and returns its exit code:

```bash
make mcp-integration-test
```

This target starts temporary PostgreSQL, Valkey, RabbitMQ, MinIO, and API containers. Use `sudo` if the current user does not have permission to access Docker:

```bash
sudo make mcp-integration-test
```

### Run a Test Subset

Run a specific test or expression directly through the integration compose file:

```bash
docker compose -f docker-compose-mcp-test.yml run --rm --build mcp-tests \
       python -m pytest -k "test_name"
```

### Clean Up Environment
The integration target stops its containers when the test run finishes. To explicitly remove stopped containers, ephemeral volumes, and the test network:

```bash
docker compose -f docker-compose-mcp-test.yml down -v
```