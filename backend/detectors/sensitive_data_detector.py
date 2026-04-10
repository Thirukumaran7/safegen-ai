import re

SENSITIVE_PATTERNS = {
    "openai_api_key":    (r'sk-[a-zA-Z0-9]{10,}', 3.5),
    "anthropic_api_key": (r'sk-ant-[a-zA-Z0-9\-]{10,}', 3.5),
    "aws_access_key":    (r'AKIA[A-Z0-9]{16}', 3.5),
    "github_token":      (r'gh[pousr]_[a-zA-Z0-9]{10,}', 3.5),
    "generic_api_key":   (r'(api[_\-]?key|api[_\-]?token)\s*[=:]\s*[a-zA-Z0-9\-_]{8,}', 3.0),
    "email_address":     (r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', 1.5),
    "phone_number":      (r'(\+\d{1,3}[\s\-]?)?\(?\d{3,5}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5}|\b\d{7,15}\b', 1.5),
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

def detect_sensitive_data(text: str) -> dict:
    types_found = []
    details = []
    total_score = 0.0
    masked_text = text

    for pii_type, (pattern, weight) in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            types_found.append(pii_type)
            total_score += weight
            friendly = PII_FRIENDLY_NAMES.get(pii_type, pii_type)
            details.append({
                "type": pii_type,
                "friendly_name": friendly,
                "count": len(matches),
                "weight": weight
            })
            # Mask matched content
            masked_text = re.sub(pattern, f"[{friendly.upper().replace(' ', '_')}_REDACTED]", masked_text, flags=re.IGNORECASE)

    total_score = round(min(10.0, total_score), 2)
    pii_count = len(types_found)
    privacy_risk, risk_message = get_privacy_risk(pii_count)

    # Anonymisation score: percentage of sensitive content masked
    original_len = len(text)
    masked_len = len(masked_text)
    if pii_count > 0 and original_len > 0:
        anon_score = round(min(100, (masked_len / original_len) * 100 * 0.5 + 50), 0)
    else:
        anon_score = 100

    return {
        "score":              total_score,
        "types_found":        types_found,
        "details":            details,
        "masked_text":        masked_text,
        "contains_sensitive": pii_count > 0,
        "anonymisation_score": anon_score,
        "pii_count":          pii_count,
        "privacy_risk":       privacy_risk,
        "risk_message":       risk_message,
        "pii_summary":        risk_message if pii_count == 0 else f"{pii_count} sensitive data type(s) detected and masked"
    }