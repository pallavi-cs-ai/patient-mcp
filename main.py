from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Patient Summary MCP")

# Debug tool to see incoming data
@mcp.tool()
def debug_payload(payload: str) -> str:
    """Echo incoming payload for debugging"""
    print("Incoming payload:", payload)
    return f"Received: {payload}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")