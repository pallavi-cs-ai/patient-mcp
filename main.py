import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Patient Summary MCP",
    json_response=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "10000"))
)

@mcp.tool()
def debug_payload(payload: str) -> str:
    """Echo payload for debugging."""
    print("Incoming:", payload)
    return payload

if __name__ == "__main__":
    mcp.run(transport="streamable-http")