def analyze_thyroid(data):
    reports = sorted(data["reports"], key=lambda x: x["date"])

    tsh_values = [r["TSH"] for r in reports]
    t3_values = [r["T3"] for r in reports]
    t4_values = [r["T4"] for r in reports]

    tsh_pattern = detect_pattern(tsh_values)
    t3_pattern = detect_pattern(t3_values)
    t4_pattern = detect_pattern(t4_values)

    crossed_threshold = any(t > 4.0 for t in tsh_values)

    return {
        "tsh_pattern": tsh_pattern,
        "t3_pattern": t3_pattern,
        "t4_pattern": t4_pattern,
        "tsh_values": tsh_values,
        "t4_values": t4_values,
        "risk": "high" if crossed_threshold else "normal"
    }

def detect_pattern(values):
    increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
    decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))

    if increasing and not decreasing:
        return "improving"
    elif decreasing and not increasing:
        return "worsening"
    else:
        if values[-1] > values[0]:
            return "fluctuating (upward tendency)"
        elif values[-1] < values[0]:
            return "fluctuating (downward tendency)"
        else:
            return "fluctuating"