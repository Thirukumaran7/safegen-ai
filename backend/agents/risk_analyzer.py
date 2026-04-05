from detectors.malware_detector import detect_malware
from detectors.sensitive_data_detector import detect_sensitive_data
from detectors.intent_classifier import classify_intent
from engine.scoring import compute_final_score
from engine.decision import make_decision

def run_risk_analysis(text: str, policy: str = "moderate", role: str = "general") -> dict:

    # Step 1 — Run all three detectors
    malware_result    = detect_malware(text)
    sensitive_result  = detect_sensitive_data(text)
    intent_result     = classify_intent(text)

    # Step 2 — Compute weighted final score
    scoring_result = compute_final_score(
        malware_score   = malware_result["score"],
        sensitive_score = sensitive_result["score"],
        intent_score    = intent_result["score"],
        role            = role
    )

    # Step 3 — Make decision based on score, policy, role
    decision_result = make_decision(
        final_score         = scoring_result["final_score"],
        policy              = policy,
        role                = role,
        sensitive_data_found = sensitive_result["contains_sensitive"],
        injection_detected  = intent_result["injection_detected"]
    )

    # Step 4 — Build explanation bullets
    explanation = []

    if malware_result["flags"]:
        explanation.append(f"Malware indicators detected: {', '.join(malware_result['flags'][:3])}")
    else:
        explanation.append("No malware indicators detected")

    if sensitive_result["types_found"]:
        explanation.append(f"Sensitive data found: {', '.join(sensitive_result['types_found'][:3])}")
    else:
        explanation.append("No sensitive data detected")

    explanation.append(f"Intent classified as: {intent_result['label']} (confidence: {intent_result['confidence']})")

    if intent_result["injection_detected"]:
        explanation.append(f"Prompt injection detected: {', '.join(intent_result['injection_patterns'][:2])}")

    explanation.append(
        f"Final score: {scoring_result['final_score']}/10 — "
        f"Malware contributed {scoring_result['contributions']['malware']}, "
        f"Sensitive contributed {scoring_result['contributions']['sensitive']}, "
        f"Intent contributed {scoring_result['contributions']['intent']}"
    )

    explanation.append(f"Decision: {decision_result['decision']} — {decision_result['reason']}")

    # Step 5 — Use masked text if sensitive data found
    display_text = sensitive_result["masked_text"] if sensitive_result["contains_sensitive"] else text

    return {
        "original_text":   text,
        "display_text":    display_text,
        "malware":         malware_result,
        "sensitive":       sensitive_result,
        "intent":          intent_result,
        "scoring":         scoring_result,
        "decision":        decision_result,
        "explanation":     explanation,
        "policy":          policy,
        "role":            role,
    }