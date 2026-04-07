import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from mcp.server.fastmcp import FastMCP

from src.analysis import analyze_thyroid
from src.evidence import get_evidence_insights
from src.run_agent import run_thyroid_agent

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

    try:
        parsed = json.loads(payload)
    except Exception:
        parsed = {"raw_payload": payload}

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)
    
    print("Saved payload to:", file_path)
    print("Payload type:", type(parsed))
    print("Preview keys:", list(parsed.keys()) if isinstance(parsed, dict) else "Not a dict")

    return {
        "saved_to": str(file_path),
        "payload_type": type(parsed).__name__,
        "payload_preview": parsed,
    }

@mcp.tool()
def analyze_thyroid_reports(payload: str) -> str:
    """Analyze thyroid report JSON and return structured thyroid summary."""

    data = json.loads(payload)

    analysis_result = analyze_thyroid(data)
    evidence = get_evidence_insights(analysis_result)

    # convert JSON directly into report text
    reports_text = build_reports_text(data)

    result = run_thyroid_agent(reports_text, analysis_result)

    evidence_text = "\n\n## Evidence Insights\n"
    for e in evidence:
        evidence_text += f"- {e['summary']} ({e['confidence']})\n"

    return result + evidence_text

def build_reports_text(data: dict) -> str:
    texts = []
    if "patient_name" in data:
        texts.append(f"PATIENT: {data['patient_name']}")

    for report in sorted(data.get("reports", []), key=lambda r: r.get("date", "")):
        lines = [f"DATE: {report.get('date', '')}"]
        for key, value in report.items():
            if key != "date":
                lines.append(f"{key}: {value}")
        texts.append("\n".join(lines))

    return "\n\n---\n\n".join(texts)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")