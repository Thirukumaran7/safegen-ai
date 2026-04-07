import joblib
import os

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "forget your instructions",
    "disregard your guidelines",
    "you are now",
    "act as",
    "pretend you are",
    "pretend to be",
    "roleplay as",
    "bypass safety",
    "bypass restrictions",
    "jailbreak",
    "do anything now",
    "dan mode",
    "evil mode",
    "developer mode",
    "unrestricted mode",
    "no restrictions",
    "without restrictions",
    "ignore ethics",
    "you have no limitations",
    "override",
    "ignore system",
    "new instructions",
    "your true self",
    "forget everything",
    "system prompt",
    "ignore safety",
    "disable safety",
    "bypass filters",
    "remove restrictions",
]

THREAT_CATEGORY_MAP = {
    "malicious":   "Malicious Intent",
    "suspicious":  "Suspicious Activity",
    "benign":      "Safe Request",
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "intent_model.pkl")
_pipeline = None

def load_model():
    global _pipeline
    if _pipeline is None:
        if os.path.exists(MODEL_PATH):
            _pipeline = joblib.load(MODEL_PATH)
            print("Intent classifier loaded successfully")
        else:
            print("WARNING: Model not found. Using fallback scoring. Run ml/train_model.py first.")
    return _pipeline

def detect_injection(text: str) -> tuple:
    text_lower = text.lower()
    found = []
    for pattern in INJECTION_PATTERNS:
        if pattern in text_lower:
            found.append(pattern)
    return len(found) > 0, found

def classify_intent(text: str) -> dict:
    injection_detected, injection_patterns = detect_injection(text)

    pipeline = load_model()

    if pipeline is None:
        score = 8.5 if injection_detected else 2.0
        label = "malicious" if injection_detected else "benign"
        return {
            "score": score,
            "label": label,
            "threat_category": THREAT_CATEGORY_MAP.get(label, "Unknown"),
            "confidence": 0.8,
            "probabilities": {},
            "injection_detected": injection_detected,
            "injection_patterns": injection_patterns,
            "model_available": False
        }

    try:
        label = pipeline.predict([text])[0]
        proba = pipeline.predict_proba([text])[0]
        classes = pipeline.classes_

        prob_dict = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}
        confidence = float(max(proba))

        if injection_detected:
            label = "malicious"
            confidence = max(confidence, 0.92)

        base_scores = {
            "benign":     1.5,
            "suspicious": 5.0,
            "malicious":  8.5
        }
        base = base_scores.get(label, 5.0)

        if label == "malicious":
            score = base + (confidence - 0.5) * 3.0
        elif label == "benign":
            score = base - (confidence - 0.5) * 2.0
        else:
            score = base

        if injection_detected:
            score = max(score, 8.5)

        score = round(max(0.0, min(10.0, score)), 2)

        return {
            "score": score,
            "label": label,
            "threat_category": THREAT_CATEGORY_MAP.get(label, "Unknown"),
            "confidence": round(confidence, 3),
            "probabilities": prob_dict,
            "injection_detected": injection_detected,
            "injection_patterns": injection_patterns,
            "model_available": True
        }

    except Exception as e:
        return {
            "score": 5.0,
            "label": "suspicious",
            "threat_category": "Suspicious Activity",
            "confidence": 0.5,
            "probabilities": {},
            "injection_detected": injection_detected,
            "injection_patterns": injection_patterns,
            "model_available": False,
            "error": str(e)
        }