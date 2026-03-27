import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Patient Summary MCP",
    json_response=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "10000"))
)

# local folder for saved samples
SAMPLES_DIR = Path("samples")
SAMPLES_DIR.mkdir(exist_ok=True)

@mcp.tool()
def debug_payload(payload: str) -> str:
    """Echo payload for debugging."""
    print("Incoming:", payload)
    return payload

@mcp.tool()
def inspect_patient_context(payload: str) -> dict[str, Any]:
    """Save incoming patient payload for inspection."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    file_path = SAMPLES_DIR / f"patient_context_{ts}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("Saved payload to:", file_path)
    print("Top-level keys:", list(payload.keys()))

    return {
        "saved_to": str(file_path),
        "top_level_keys": list(payload.keys()),
        "payload_preview": payload,
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")