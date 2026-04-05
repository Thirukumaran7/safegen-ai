POLICY_THRESHOLDS = {
    "strict": {
        "student": {
            "allow_max":    2.0,
            "restrict_max": 4.5,
            "redact_max":   6.5,
        },
        "general": {
            "allow_max":    2.5,
            "restrict_max": 5.0,
            "redact_max":   7.0,
        },
        "expert": {
            "allow_max":    3.5,
            "restrict_max": 6.0,
            "redact_max":   8.0,
        },
    },
    "moderate": {
        "student": {
            "allow_max":    3.0,
            "restrict_max": 5.5,
            "redact_max":   7.5,
        },
        "general": {
            "allow_max":    3.5,
            "restrict_max": 6.0,
            "redact_max":   8.0,
        },
        "expert": {
            "allow_max":    4.5,
            "restrict_max": 7.0,
            "redact_max":   8.5,
        },
    },
    "open": {
        "student": {
            "allow_max":    4.0,
            "restrict_max": 6.5,
            "redact_max":   8.5,
        },
        "general": {
            "allow_max":    5.0,
            "restrict_max": 7.0,
            "redact_max":   9.0,
        },
        "expert": {
            "allow_max":    6.0,
            "restrict_max": 8.0,
            "redact_max":   9.5,
        },
    }
}

def get_thresholds(policy: str, role: str) -> dict:
    policy_config = POLICY_THRESHOLDS.get(policy, POLICY_THRESHOLDS["moderate"])
    thresholds = policy_config.get(role, policy_config["general"])
    return thresholds