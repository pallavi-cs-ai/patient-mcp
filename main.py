from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("Patient Summary MCP")

@mcp.tool()
def debug_payload(payload: str) -> str:
    return payload


if __name__ == "__main__":
    # IMPORTANT: set env BEFORE run
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = os.environ.get("PORT", "10000")

    mcp.run(transport="streamable-http")