ROLE_WEIGHTS = {
    "student": {
        "malware":   0.45,
        "sensitive": 0.30,
        "intent":    0.25,
    },
    "general": {
        "malware":   0.40,
        "sensitive": 0.30,
        "intent":    0.30,
    },
    "expert": {
        "malware":   0.35,
        "sensitive": 0.25,
        "intent":    0.40,
    }
}

def compute_final_score(
    malware_score: float,
    sensitive_score: float,
    intent_score: float,
    role: str = "general"
) -> dict:

    weights = ROLE_WEIGHTS.get(role, ROLE_WEIGHTS["general"])

    final = (
        weights["malware"]   * malware_score +
        weights["sensitive"] * sensitive_score +
        weights["intent"]    * intent_score
    )

    final = round(min(10.0, max(0.0, final)), 2)

    return {
        "final_score": final,
        "weights_used": weights,
        "contributions": {
            "malware":   round(weights["malware"]   * malware_score,   2),
            "sensitive": round(weights["sensitive"] * sensitive_score, 2),
            "intent":    round(weights["intent"]    * intent_score,    2),
        }
    }