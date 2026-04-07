from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import json
import os
from .evidence import get_evidence_insights
from .analysis import analyze_thyroid

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

def run_thyroid_agent(reports_text: str, analysis_result: dict) -> str:
    prompt = f"""
You are an evidence-aware clinical AI assistant.

Use the pre-computed structured analysis below as the source of truth.
Do NOT override it.
Do NOT recompute the trend or pattern from scratch.
Your job is to explain the findings clearly, cautiously, and consistently with the structured analysis.

Structured analysis:
- TSH Direction: {analysis_result["tsh_direction"]}
- T3 Direction: {analysis_result["t3_direction"]}
- T4 Direction: {analysis_result["t4_direction"]}
- TSH Pattern: {analysis_result["tsh_pattern"]}
- T3 Pattern: {analysis_result["t3_pattern"]}
- T4 Pattern: {analysis_result["t4_pattern"]}
- Risk / Concern Level: {analysis_result["risk"]}

Instructions:
- Use the provided structured analysis exactly as given.
- Do not contradict or override the structured analysis.
- Write a concise, clinically appropriate explanation.
- Focus only on observable lab patterns and uncertainty.
- Do not invent symptoms, diagnoses, causes, treatments, or interventions not present in the reports.
- If the underlying cause cannot be determined, explicitly state that it is uncertain.
- Do not show intermediate steps.

Section Requirements:
1. Chronological Table
   - List the report dates and exact TSH, T3, and T4 values as provided.
2. Overall Trend
   - Summarize the overall behavior using the structured analysis.
3. Pattern
   - Describe the TSH, T3, and T4 patterns exactly as provided in the structured analysis.
4. Most Significant Change
   - Highlight the single most important observed lab change.
5. Risk / Concern Level
   - Use the provided risk level exactly.
6. Clinical Summary
   - Explain why the observed longitudinal pattern is clinically meaningful.
   - If the pattern is fluctuating, highlight instability and reduced confidence in a clear progression.
   - If the pattern is improving or worsening, explain why repeated directional change across timepoints is meaningful.
   - If the pattern is improving or worsening, use the phrase "consistent directional change across timepoints".
   - Do NOT use phrases like "repeated directional change" for consistent trends.
   - Use "repeated changes" only when describing fluctuating patterns.
7. Evidence-Informed Considerations
   - Provide discussion points only.
   - Only describe observable patterns and uncertainty.
   - Do NOT mention possible causes, mechanisms, or physiological explanations.
   - Only describe what is observable from the reported values and what remains uncertain.
   - Do NOT suggest any actions (e.g., monitoring, evaluation, intervention).
   - Use neutral phrasing such as "remains uncertain" or "does not allow clear determination".
8. Disclaimer
   - State that the analysis is based only on the provided reports and does not replace clinical judgment.

Critical Rule:
- Do not reinterpret the raw numeric trend if it conflicts with the provided structured analysis.

Return only these sections:

1. Chronological Table
2. Overall Trend
3. Pattern
4. Most Significant Change
5. Risk / Concern Level
6. Clinical Summary
7. Evidence-Informed Considerations
8. Disclaimer

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
    json_path = "../reports/patient_fluctuating.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    reports_text = load_reports(json_path)

    analysis_result = analyze_thyroid(data)
    evidence = get_evidence_insights(analysis_result)

    result = run_thyroid_agent(reports_text, analysis_result)

    evidence_text = "\n\n## Evidence Insights\n"
    for e in evidence:
        evidence_text += f"- {e['summary']} ({e['confidence']})\n"

    final_output = result + evidence_text
    print(final_output)

if __name__ == "__main__":
    main()