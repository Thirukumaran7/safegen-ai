from .policy import get_thresholds

DECISION_DESCRIPTIONS = {
    "ALLOW":    "Input is safe. Full response provided.",
    "RESTRICT": "Input is borderline. High level response only, no technical details.",
    "REDACT":   "Sensitive data detected and masked. Partial response provided.",
    "BLOCK":    "Input violates safety policy. Request denied.",
}

def make_decision(
    final_score: float,
    policy: str,
    role: str,
    sensitive_data_found: bool = False,
    injection_detected: bool = False
) -> dict:

    # Injection always results in immediate BLOCK
    if injection_detected:
        return {
            "decision": "BLOCK",
            "reason": "Prompt injection attempt detected",
            "description": DECISION_DESCRIPTIONS["BLOCK"],
            "thresholds_used": get_thresholds(policy, role),
            "override": "injection_detected"
        }

    thresholds = get_thresholds(policy, role)

    if final_score <= thresholds["allow_max"]:
        decision = "ALLOW"
        reason = f"Score {final_score} is within safe threshold of {thresholds['allow_max']}"
    elif final_score <= thresholds["restrict_max"]:
        decision = "RESTRICT"
        reason = f"Score {final_score} exceeds allow threshold of {thresholds['allow_max']}"
    elif final_score <= thresholds["redact_max"]:
        decision = "REDACT"
        reason = f"Score {final_score} exceeds restrict threshold of {thresholds['restrict_max']}"
    else:
        decision = "BLOCK"
        reason = f"Score {final_score} exceeds redact threshold of {thresholds['redact_max']}"

    # If sensitive data found, minimum decision is REDACT
    if sensitive_data_found and decision == "ALLOW":
        decision = "REDACT"
        reason = "Sensitive data detected in input"

    if sensitive_data_found and decision == "RESTRICT":
        decision = "REDACT"
        reason = "Sensitive data detected, upgrading to REDACT"

    return {
        "decision": decision,
        "reason": reason,
        "description": DECISION_DESCRIPTIONS[decision],
        "thresholds_used": thresholds,
        "override": None
    }