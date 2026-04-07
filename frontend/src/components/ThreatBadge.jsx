const SEVERITY_COLORS = {
  Critical: { bg: "#2d0f0f", border: "#742a2a", text: "#fc8181", dot: "#fc0000" },
  High:     { bg: "#2d1a0f", border: "#744210", text: "#f6ad55", dot: "#f97316" },
  Medium:   { bg: "#0d1f3c", border: "#2a4a8a", text: "#63b3ed", dot: "#3b82f6" },
  Low:      { bg: "#0d2b1a", border: "#22543d", text: "#68d391", dot: "#22c55e" },
  None:     { bg: "#1a1d2e", border: "#2d3748", text: "#718096", dot: "#718096" },
}

const MALWARE_ICONS = {
  Ransomware:        "🔒",
  Keylogger:         "⌨️",
  Trojan:            "🎭",
  Rootkit:           "🕳️",
  Botnet:            "🕸️",
  Spyware:           "👁️",
  Adware:            "📢",
  Cryptominer:       "⛏️",
  Worm:              "🪱",
  Virus:             "🦠",
  RAT:               "🐀",
  Dropper:           "💧",
  Fileless_Malware:  "👻",
  Backdoor:          "🚪",
  Exploit:           "💥",
  Social_Engineering:"🎣",
  None:              "✅",
}

export default function ThreatBadge({ malwareType, malwareCategory, severity, description }) {
  if (!malwareType || malwareType === "None") {
    return (
      <div style={{ background: "#0d2b1a", border: "1px solid #22543d", borderRadius: "10px", padding: "14px 16px", display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ fontSize: "20px" }}>✅</span>
        <div>
          <div style={{ fontSize: "13px", fontWeight: "600", color: "#68d391" }}>No Threat Detected</div>
          <div style={{ fontSize: "11px", color: "#718096", marginTop: "2px" }}>Input does not match any malware taxonomy</div>
        </div>
      </div>
    )
  }

  const colors = SEVERITY_COLORS[severity] || SEVERITY_COLORS.None
  const icon = MALWARE_ICONS[malwareType?.replace(" ", "_")] || "⚠️"

  return (
    <div style={{ background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: "10px", padding: "14px 16px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
        <span style={{ fontSize: "20px" }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "14px", fontWeight: "700", color: colors.text }}>{malwareType}</span>
            <span style={{ fontSize: "10px", background: colors.border, color: colors.text, padding: "2px 6px", borderRadius: "10px" }}>{severity}</span>
          </div>
          <div style={{ fontSize: "11px", color: "#718096", marginTop: "1px" }}>{malwareCategory}</div>
        </div>
      </div>
      <div style={{ fontSize: "12px", color: "#a0aec0", lineHeight: "1.5", paddingLeft: "30px" }}>{description}</div>
    </div>
  )
}