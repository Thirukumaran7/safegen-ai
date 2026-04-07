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
    "ssn":               (r'\b\d{3}-\d{2}-\d{4}\b', 4.0),
    "national_id":       (r'\b\d{12}\b', 2.0),
}

PRIVACY_RISK_LEVELS = {
    (0, 0):     ("None",   "No sensitive data detected"),
    (1, 1):     ("Low",    "1 type of sensitive data detected"),
    (2, 3):     ("Medium", "Multiple sensitive data types detected"),
    (4, 99):    ("High",   "Critical sensitive data detected"),
}

PII_FRIENDLY_NAMES = {
    "openai_api_key":    "OpenAI API Key",
    "anthropic_api_key": "Anthropic API Key",
    "aws_access_key":    "AWS Access Key",
    "github_token":      "GitHub Token",
    "generic_api_key":   "API Key",
    "email_address":     "Email Address",
    "phone_number":      "Phone Number",
    "credit_card":       "Credit Card Number",
    "password_in_text":  "Password",
    "ip_address":        "IP Address",
    "bearer_token":      "Bearer Token",
    "private_key":       "Private Key",
    "jwt_token":         "JWT Token",
    "ssn":               "Social Security Number",
    "national_id":       "National ID Number",
}

def get_privacy_risk(count: int) -> tuple:
    for (low, high), (level, message) in PRIVACY_RISK_LEVELS.items():
        if low <= count <= high:
            return level, message
    return "High", "Multiple critical data types detected"

def get_anonymisation_score(found_count: int, total_patterns: int) -> int:
    if found_count == 0:
        return 100
    masked_percentage = ((total_patterns - found_count) / total_patterns) * 100
    return max(0, min(100, int(masked_percentage)))

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

def build_pii_summary(found_types: list) -> str:
    if not found_types:
        return "No sensitive data detected"
    friendly = [PII_FRIENDLY_NAMES.get(t, t) for t in found_types]
    if len(friendly) == 1:
        return f"{friendly[0]} detected and masked"
    elif len(friendly) == 2:
        return f"{friendly[0]} and {friendly[1]} detected and masked"
    else:
        return f"{', '.join(friendly[:-1])}, and {friendly[-1]} detected and masked"

def detect_sensitive_data(text: str) -> dict:
    found_types = []
    raw_score = 0.0
    details = []
    total_count = 0

    for data_type, (pattern, weight) in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_types.append(data_type)
            raw_score += weight
            total_count += len(matches)
            details.append(f"{PII_FRIENDLY_NAMES.get(data_type, data_type)}: {len(matches)} instance(s) found")

    normalised = min(10.0, (raw_score / 7.0) * 10.0)
    privacy_risk, risk_message = get_privacy_risk(len(found_types))
    anonymisation_score = get_anonymisation_score(len(found_types), len(SENSITIVE_PATTERNS))
    pii_summary = build_pii_summary(found_types)

    return {
        "score": round(normalised, 2),
        "types_found": found_types,
        "details": details,
        "masked_text": mask_text(text),
        "contains_sensitive": len(found_types) > 0,
        "anonymisation_score": anonymisation_score,
        "pii_count": total_count,
        "privacy_risk": privacy_risk,
        "risk_message": risk_message,
        "pii_summary": pii_summary
    }