import re

SENSITIVE_PATTERNS = {
    "openai_api_key":    (r'sk-[a-zA-Z0-9]{10,}', 3.5),
    "anthropic_api_key": (r'sk-ant-[a-zA-Z0-9\-]{10,}', 3.5),
    "aws_access_key":    (r'AKIA[A-Z0-9]{16}', 3.5),
    "github_token":      (r'gh[pousr]_[a-zA-Z0-9]{10,}', 3.5),
    "generic_api_key":   (r'(api[_\-]?key|api[_\-]?token)\s*[=:]\s*[a-zA-Z0-9\-_]{8,}', 3.0),
    "email_address":     (r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', 1.5),
    "phone_number":      (r'(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', 1.5),
    "credit_card":       (r'(?:\d{4}[\s\-]?){3}\d{4}', 3.0),
    "password_in_text":  (r'(password|passwd|pwd|pass)\s*[=:is]+\s*\S{4,}', 3.0),
    "ip_address":        (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 1.0),
    "bearer_token":      (r'Bearer\s+[a-zA-Z0-9\-_\.]{10,}', 3.5),
    "private_key":       (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', 4.0),
    "jwt_token":         (r'eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+', 3.0),
}

def mask_text(text: str) -> str:
    masked = text
    for name, (pattern, _) in SENSITIVE_PATTERNS.items():
        masked = re.sub(
            pattern,
            f"[{name.upper()}_REDACTED]",
            masked,
            flags=re.IGNORECASE
        )
    return masked

def detect_sensitive_data(text: str) -> dict:
    found_types = []
    raw_score = 0.0
    details = []

    for data_type, (pattern, weight) in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_types.append(data_type)
            raw_score += weight
            details.append(f"{data_type}: {len(matches)} instance(s) found")

    normalised = min(10.0, (raw_score / 7.0) * 10.0)

    return {
        "score": round(normalised, 2),
        "types_found": found_types,
        "details": details,
        "masked_text": mask_text(text),
        "contains_sensitive": len(found_types) > 0
    }