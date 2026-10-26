import logging
import os
import time
import httpx2
import requests
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAPI_DOCS_URL = os.getenv(
    "OPENAPI_DOCS_URL", "http://api:8000/api/schema/?format=json"
)
PLANE_API_URL = os.getenv("PLANE_API_URL", "http://api:8000/api/v1")


def fetch_openapi_spec(max_retries: int = 5, retry_interval: int = 10) -> dict | None:
    """Fetch the OpenAPI specification from the backend with a resilient retry loop."""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Loading OpenAPI documentation (Attempt {attempt}/{max_retries})..."
            )
            response = requests.get(OPENAPI_DOCS_URL, timeout=10)
            response.raise_for_status()
            logger.info("Successfully loaded OpenAPI documentation.")
            return response.json()

        except Exception as e:
            if attempt == max_retries:
                logger.error(
                    f"Failed to load OpenAPI documentation after {max_retries} attempts: {e}"
                )
                return None
            logger.warning(f"API not ready yet, retrying in {retry_interval}s...")
            time.sleep(retry_interval)
    return None


def mcp_factory():
    openapi_spec = fetch_openapi_spec()
    if not openapi_spec:
        logger.error(
            "Exiting: Could not initialize MCP server without OpenAPI specification."
        )
        return

    client = httpx2.AsyncClient(base_url=PLANE_API_URL)

    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec, client=client, name="PlaneAI MCP Server"
    )

    return mcp


if __name__ == "__main__":
    mcp = mcp_factory()
    mcp.run()
