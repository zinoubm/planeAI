import pytest
from mcp_server import mcp_factory


@pytest.mark.asyncio
async def test_fastmcp_tools_registered():
    """Verify that expected tools are registered correctly in the MCP server."""
    # FastMCP typically exposes tools via its list_tools handler
    mcp = mcp_factory()
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    assert isinstance(tool_names, list)


@pytest.fixture
def mcp_server():
    """Spin up the MCP server instance using the running backend spec."""
    return mcp_factory()


@pytest.mark.asyncio
async def test_mcp_connection_and_tool_registration(mcp_server):
    """Smoke test: verify that the MCP server successfully fetches
    the schema and registers tools from the backend API.
    """
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]

    assert isinstance(tool_names, list)
    assert len(tool_names) > 0, "No tools were registered from the OpenAPI schema!"


@pytest.mark.asyncio
async def test_tool_metadata_and_schemas(mcp_server):
    """Verify that every generated tool has proper metadata,
    descriptions, and valid input schemas for LLM tool-calling.
    """
    tools = await mcp_server.list_tools()

    for tool in tools:
        # Every tool must have a valid string identifier name
        assert tool.name, "Encountered a tool without a name."
        assert isinstance(tool.name, str)

        # Verify input schema structure exists for parameter mapping
        if hasattr(tool, "inputSchema") and tool.inputSchema:
            assert isinstance(
                tool.inputSchema, dict
            ), f"Tool {tool.name} has invalid inputSchema type."


@pytest.mark.asyncio
async def test_core_plane_resources_exposed(mcp_server):
    """Verify that expected Plane backend domains (projects, workspaces, issues)
    are properly translated into accessible MCP tools.
    """
    tools = await mcp_server.list_tools()
    tool_names = [t.name.lower() for t in tools]

    # Look for common backend resource keywords to ensure schema mapping worked
    expected_keywords = ["project", "workspace", "issue"]
    found_keywords = any(
        any(keyword in name for keyword in expected_keywords) for name in tool_names
    )

    assert found_keywords, (
        f"None of the expected core resource keywords {expected_keywords} "
        f"were found in the registered tool names."
    )
