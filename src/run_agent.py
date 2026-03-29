from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import json
import os
from evidence import get_evidence_insights
from analysis import detect_pattern

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_reports(path: str) -> str:
    report_path = Path(path)
    if report_path.is_file() and report_path.suffix.lower() == ".json":
        with report_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

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

    return ""

def extract_values(data):
    reports = sorted(data["reports"], key=lambda x: x["date"])

    tsh = [r["TSH"] for r in reports]
    t3 = [r["T3"] for r in reports]
    t4 = [r["T4"] for r in reports]

    return tsh, t3, t4

def run_thyroid_agent(reports_text: str) -> str:
    prompt = f"""
You are an evidence-aware clinical AI assistant.

Analyze the provided thyroid reports for one patient over time.

Instructions:
- Extract all report dates and lab values exactly as written.
- Order the reports chronologically.
- Compare TSH, T3, and T4 across time.
- Identify the overall trend.
- Identify the pattern using one or more of: stable, improving, worsening, fluctuating, threshold crossing.
- State the single most significant change.
- Assign a concern level: low, moderate, or high.

Clinical Summary Requirements:
- Must interpret the data, not just restate values.
- Must explain why the pattern is clinically meaningful.
- Must explicitly explain whether the pattern is consistent or fluctuating.
- If fluctuating, must highlight instability and reduced confidence in a clear trend.
- Must explain why multiple timepoints improve interpretation compared to a single measurement.
- Must indicate level of concern cautiously (e.g., “suggestive of”, “may indicate”).
- Must NOT introduce symptoms, diagnoses, or causes not present in the reports.

Evidence Requirements:
- Provide evidence-informed considerations as discussion points only.
- Do NOT prescribe treatment.
- Do NOT introduce causes, treatments, or interventions unless explicitly stated in the reports.
- Avoid speculative explanations.
- Focus on interpreting the observed data trends only.
- If the underlying cause cannot be determined, explicitly state that it is uncertain.
- Do NOT mention specific diagnoses or conditions unless explicitly confirmed by the data.
- Focus only on patterns observed in the lab values.
- Evidence-Informed Considerations must NOT introduce physiological mechanisms, organs, or conditions not explicitly present in the data.
- Only describe observable patterns and uncertainty.

Output Format Rules:
- Do not show intermediate steps.
- Return only the final answer in these sections:

1. Chronological Table
2. Overall Trend
3. Pattern
4. Most Significant Change
5. Risk / Concern Level
6. Clinical Summary
7. Evidence-Informed Considerations
8. Disclaimer

Overall Trend Rule:
- The "Overall Trend" must reflect whether the data is consistent or fluctuating.
- If any reversal in direction exists, describe the trend as "fluctuating" rather than simply increasing or decreasing.

Clinical Summary Rule:
- Must explicitly explain whether the pattern is consistent or fluctuating.
- If fluctuating, must highlight instability and reduced confidence in a clear trend.
- Must explain why multiple timepoints improve interpretation compared to a single measurement.

Evidence Restriction Rule:
- Evidence-Informed Considerations must NOT introduce physiological mechanisms, organs, or conditions not explicitly present in the data.
- Only describe observable patterns and uncertainty.

Additional Rules:
- If a statement is not directly supported by the reports, label it as uncertain.
- Prefer cautious, clinically appropriate language over strong claims.
- Highlight why multiple timepoints provide stronger clinical signal than a single measurement.
- All numerical values must match the input exactly. Do not approximate or alter values.
- If values remain constant, explicitly state that they are stable.
- The "Overall Trend" must reflect whether the data is consistent or fluctuating.
- If any reversal in direction exists, describe the trend as "fluctuating" rather than simply increasing or decreasing.

Trend and Pattern Decision Rules:
- Evaluate each consecutive interval separately.
- For each lab value, determine whether it increases, decreases, or stays stable between each pair of consecutive timepoints.
- If all consecutive changes move in the same direction, the pattern may be labeled as improving or worsening.
- If any reversal occurs across timepoints, the pattern must be labeled as fluctuating.
- If the pattern is fluctuating, do not describe it as consistently worsening or consistently improving.
- If the pattern is fluctuating but the final value is higher or lower than the initial value, you may say "fluctuating with an overall upward tendency" or "fluctuating with an overall downward tendency."

Reports:
{reports_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an evidence-aware clinical AI assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content

def main():
    reports_text = load_reports("../reports/patient_improving.json")
    result = run_thyroid_agent(reports_text)

    # fake minimal structure for evidence mapping
    analysis_result = {
        "overall_trend": "worsening",
        "pattern": "consistent increase"
    }

    evidence = get_evidence_insights(analysis_result)

    # convert evidence to readable text
    evidence_text = "\n\n## Evidence Insights\n"
    for e in evidence:
        evidence_text += f"- {e['summary']} ({e['confidence']})\n"

    final_output = result + evidence_text

    print(final_output)

if __name__ == "__main__":
    main()