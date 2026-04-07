const RISK_COLORS = {
  High:   { text: "#fc8181", bg: "#2d0f0f", border: "#742a2a", bar: "#fc8181" },
  Medium: { text: "#f6ad55", bg: "#2d1a0f", border: "#744210", bar: "#f6ad55" },
  Low:    { text: "#68d391", bg: "#0d2b1a", border: "#22543d", bar: "#68d391" },
  None:   { text: "#718096", bg: "#1a1d2e", border: "#2d3748", bar: "#4a5568" },
}

const PII_ICONS = {
  openai_api_key:    "🔑",
  anthropic_api_key: "🔑",
  aws_access_key:    "🔑",
  github_token:      "🔑",
  generic_api_key:   "🔑",
  email_address:     "📧",
  phone_number:      "📱",
  credit_card:       "💳",
  password_in_text:  "🔐",
  ip_address:        "🌐",
  bearer_token:      "🎫",
  private_key:       "🗝️",
  jwt_token:         "🎫",
  ssn:               "🪪",
  national_id:       "🪪",
}

const PII_NAMES = {
  openai_api_key:    "OpenAI API Key",
  anthropic_api_key: "Anthropic API Key",
  aws_access_key:    "AWS Access Key",
  github_token:      "GitHub Token",
  generic_api_key:   "API Key",
  email_address:     "Email Address",
  phone_number:      "Phone Number",
  credit_card:       "Credit Card",
  password_in_text:  "Password",
  ip_address:        "IP Address",
  bearer_token:      "Bearer Token",
  private_key:       "Private Key",
  jwt_token:         "JWT Token",
  ssn:               "SSN",
  national_id:       "National ID",
}

export default function AnonymisationPanel({ anonymisationScore, privacyRisk, piiCount, typesFound, piiSummary }) {
  const colors = RISK_COLORS[privacyRisk] || RISK_COLORS.None

  return (
    <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "16px 20px", border: "1px solid #2d3748" }}>
      <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        Privacy Protection
      </div>

      {/* Anonymisation score bar */}
      <div style={{ marginBottom: "12px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
          <span style={{ fontSize: "12px", color: "#718096" }}>Anonymisation Score</span>
          <span style={{ fontSize: "16px", fontWeight: "700", color: colors.text }}>{anonymisationScore}%</span>
        </div>
        <div style={{ height: "8px", background: "#2d3748", borderRadius: "4px", overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${anonymisationScore}%`, background: colors.bar, borderRadius: "4px", transition: "width 0.5s ease" }} />
        </div>
      </div>

      {/* Privacy risk level */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
        <div style={{ background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: "6px", padding: "3px 10px" }}>
          <span style={{ fontSize: "12px", fontWeight: "600", color: colors.text }}>
            {privacyRisk} Risk
          </span>
        </div>
        {piiCount > 0 && (
          <span style={{ fontSize: "12px", color: "#718096" }}>
            {piiCount} item{piiCount > 1 ? "s" : ""} detected and masked
          </span>
        )}
      </div>

      {/* PII types found */}
      {typesFound && typesFound.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          {typesFound.map((type, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "#a0aec0" }}>
              <span>{PII_ICONS[type] || "⚠️"}</span>
              <span>{PII_NAMES[type] || type}</span>
              <span style={{ marginLeft: "auto", fontSize: "10px", color: "#4a5568", background: "#0f1117", padding: "1px 6px", borderRadius: "10px" }}>masked</span>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ fontSize: "12px", color: "#4a5568" }}>No personal or sensitive data found in input</div>
      )}
    </div>
  )
}