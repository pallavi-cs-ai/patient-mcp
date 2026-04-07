
def detect_direction(values):
    increasing = all(values[i] <= values[i + 1] for i in range(len(values) - 1))
    decreasing = all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    if increasing and not decreasing:
        return "increasing"
    elif decreasing and not increasing:
        return "decreasing"
    else:
        if values[-1] > values[0]:
            return "fluctuating (upward tendency)"
        elif values[-1] < values[0]:
            return "fluctuating (downward tendency)"
        else:
            return "fluctuating"


def interpret_marker(marker, direction):
    if marker == "TSH":
        if direction == "decreasing":
            return "improving"
        elif direction == "increasing":
            return "worsening"
        elif "downward tendency" in direction:
            return "fluctuating (overall improving tendency)"
        elif "upward tendency" in direction:
            return "fluctuating (overall worsening tendency)"
        return "fluctuating"

    if marker in ["T3", "T4"]:
        if direction == "increasing":
            return "improving"
        elif direction == "decreasing":
            return "worsening"
        elif "upward tendency" in direction:
            return "fluctuating (overall improving tendency)"
        elif "downward tendency" in direction:
            return "fluctuating (overall worsening tendency)"
        return "fluctuating"

    return direction


def analyze_thyroid(data):
    reports = sorted(data["reports"], key=lambda x: x["date"])

    tsh_values = [r["TSH"] for r in reports]
    t3_values = [r["T3"] for r in reports]
    t4_values = [r["T4"] for r in reports]

    tsh_direction = detect_direction(tsh_values)
    t3_direction = detect_direction(t3_values)
    t4_direction = detect_direction(t4_values)

    tsh_pattern = interpret_marker("TSH", tsh_direction)
    t3_pattern = interpret_marker("T3", t3_direction)
    t4_pattern = interpret_marker("T4", t4_direction)

    # simple overall risk
    crossed_threshold = any(t > 4.0 for t in tsh_values)
    if "improving" in tsh_pattern and "improving" in t4_pattern:
        risk = "low"
    elif "fluctuating" in tsh_pattern or "fluctuating" in t4_pattern:
        risk = "moderate"
    else:
        risk = "high" if crossed_threshold else "moderate"

    return {
        "tsh_values": tsh_values,
        "t3_values": t3_values,
        "t4_values": t4_values,
        "tsh_direction": tsh_direction,
        "t3_direction": t3_direction,
        "t4_direction": t4_direction,
        "tsh_pattern": tsh_pattern,
        "t3_pattern": t3_pattern,
        "t4_pattern": t4_pattern,
        "risk": risk,
    }