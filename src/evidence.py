EVIDENCE_DB = {
    "hypothyroid_trend": {
        "summary": "Elevated TSH with low or declining T4 is commonly associated with hypothyroid patterns.",
        "source": "General clinical guidelines (e.g., ATA)",
        "confidence": "high"
    },
    "longitudinal_consistent": {
        "summary": "Consistent directional change across multiple timepoints is more clinically significant than a single abnormal value.",
        "source": "Clinical practice principle",
        "confidence": "high"
    },
    "fluctuating_pattern": {
        "summary": "Fluctuating values across multiple timepoints indicate variability and reduce confidence in a stable trend.",
        "source": "Clinical interpretation principle",
        "confidence": "high"
    },
    "stable_t3": {
        "summary": "T3 levels may remain stable in early or evolving thyroid-related changes.",
        "source": "Endocrine physiology understanding",
        "confidence": "moderate"
    }
}

def get_evidence_insights(analysis_result):
    insights = []

    pattern = analysis_result.get("pattern", "").lower()

    if "fluctuating" in pattern:
        insights.append(EVIDENCE_DB["fluctuating_pattern"])
    else:
        insights.append(EVIDENCE_DB["longitudinal_consistent"])

    if "tsh" in pattern or "t4" in pattern:
        insights.append(EVIDENCE_DB["hypothyroid_trend"])

    insights.append(EVIDENCE_DB["stable_t3"])

    return insights