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
    "fluctuating_instability": {
        "summary": "Fluctuating values across multiple timepoints indicate variability and reduce confidence in a consistent clinical trend.",
        "source": "Clinical interpretation principle",
        "confidence": "high"
    },
    "improving_trend": {
        "summary": "Consistent improvement across multiple timepoints strengthens confidence in a true improving trend rather than isolated variation.",
        "source": "Clinical interpretation principle",
        "confidence": "high"
    }
}


def get_evidence_insights(analysis_result):
    insights = []

    tsh_pattern = analysis_result.get("tsh_pattern", "").lower()
    t4_pattern = analysis_result.get("t4_pattern", "").lower()

    # Main evidence based on TSH pattern
    if "fluctuating" in tsh_pattern:
        insights.append(EVIDENCE_DB["fluctuating_instability"])
    elif "improving" in tsh_pattern:
        insights.append(EVIDENCE_DB["improving_trend"])
    else:
        insights.append(EVIDENCE_DB["longitudinal_consistent"])

    # Add hypothyroid evidence only for worsening thyroid pattern
    if tsh_pattern == "worsening" and t4_pattern == "worsening":
        insights.append(EVIDENCE_DB["hypothyroid_trend"])

    return insights