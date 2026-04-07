from detectors.malware_detector import detect_malware
from detectors.sensitive_data_detector import detect_sensitive_data
from detectors.intent_classifier import classify_intent
from engine.scoring import compute_final_score
from engine.decision import make_decision
import os

def run_risk_analysis(text: str, policy: str = "moderate", role: str = "general") -> dict:

    # Step 1 — Run all three detectors
    malware_result   = detect_malware(text)
    sensitive_result = detect_sensitive_data(text)
    intent_result    = classify_intent(text)

    # Step 2 — Compute weighted final score
    scoring_result = compute_final_score(
        malware_score   = malware_result["score"],
        sensitive_score = sensitive_result["score"],
        intent_score    = intent_result["score"],
        role            = role
    )

    # Step 3 — Make decision
    decision_result = make_decision(
        final_score          = scoring_result["final_score"],
        policy               = policy,
        role                 = role,
        sensitive_data_found = sensitive_result["contains_sensitive"],
        injection_detected   = intent_result["injection_detected"]
    )

    # Step 4 — Build explanation
    explanation = []

    if malware_result["flags"]:
        explanation.append(f"Malware indicators detected: {', '.join(malware_result['flags'][:3])}")
        explanation.append(f"Threat type identified: {malware_result['malware_type']} — {malware_result['description']}")
    else:
        explanation.append("No malware indicators detected")

    if sensitive_result["types_found"]:
        explanation.append(f"Privacy: {sensitive_result['pii_summary']}")
        explanation.append(f"Anonymisation score: {sensitive_result['anonymisation_score']}% — Privacy risk: {sensitive_result['privacy_risk']}")
    else:
        explanation.append("No sensitive data detected")

    explanation.append(f"Intent: {intent_result['threat_category']} (confidence: {intent_result['confidence']})")

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
        "original_text":  text,
        "display_text":   display_text,
        "malware":        malware_result,
        "sensitive":      sensitive_result,
        "intent":         intent_result,
        "scoring":        scoring_result,
        "decision":       decision_result,
        "explanation":    explanation,
        "policy":         policy,
        "role":           role,
    }

def analyze_image(image_base64: str, policy: str = "moderate", role: str = "general") -> dict:
    try:
        from google import genai
        from dotenv import load_dotenv
        load_dotenv()

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        prompt = """Analyze this image for safety concerns. Check for:
1. NSFW or adult content
2. Violent or graphic content
3. Visible personal information (faces, ID cards, documents with names/addresses)
4. Malware-related content (screenshots of malicious code, phishing pages)
5. Hate speech or offensive symbols

Respond in this exact format:
SAFE: yes/no
ISSUES: list any issues found or 'none'
SEVERITY: Critical/High/Medium/Low/None
RECOMMENDATION: BLOCK/REDACT/RESTRICT/ALLOW"""

        import base64 as b64
        image_bytes = b64.b64decode(image_base64)

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}},
                        {"text": prompt}
                    ]
                }
            ]
        )

        response_text = response.text
        lines = response_text.strip().split('\n')
        result = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()

        is_safe = result.get("SAFE", "no").lower() == "yes"
        severity = result.get("SEVERITY", "None")
        recommendation = result.get("RECOMMENDATION", "RESTRICT")
        issues = result.get("ISSUES", "none")

        severity_scores = {"Critical": 9.0, "High": 7.0, "Medium": 5.0, "Low": 3.0, "None": 0.0}
        score = severity_scores.get(severity, 0.0)

        return {
            "input_type": "image",
            "is_safe": is_safe,
            "issues": issues,
            "severity": severity,
            "score": score,
            "decision": recommendation,
            "explanation": [f"Image analysis: {issues}", f"Severity: {severity}", f"Recommendation: {recommendation}"],
            "policy": policy,
            "role": role
        }

    except Exception as e:
        return {
            "input_type": "image",
            "is_safe": False,
            "issues": f"Analysis error: {str(e)}",
            "severity": "Unknown",
            "score": 5.0,
            "decision": "RESTRICT",
            "explanation": ["Image analysis failed — defaulting to RESTRICT"],
            "policy": policy,
            "role": role
        }

def analyze_document(content: str, filename: str = "document", policy: str = "moderate", role: str = "general") -> dict:
    # Run the same text analysis pipeline on document content
    analysis = run_risk_analysis(text=content, policy=policy, role=role)

    # Add document specific info
    word_count = len(content.split())
    char_count = len(content)

    analysis["input_type"] = "document"
    analysis["filename"] = filename
    analysis["word_count"] = word_count
    analysis["char_count"] = char_count

    return analysis