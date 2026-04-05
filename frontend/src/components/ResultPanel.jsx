import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

const DECISION_COLORS = {
  ALLOW:    { bg: "#0d2b1a", border: "#22543d", text: "#68d391", badge: "#276749" },
  RESTRICT: { bg: "#2d2006", border: "#744210", text: "#f6ad55", badge: "#7b4f12" },
  REDACT:   { bg: "#0d1f3c", border: "#2a4a8a", text: "#63b3ed", badge: "#2b4c8c" },
  BLOCK:    { bg: "#2d0f0f", border: "#742a2a", text: "#fc8181", badge: "#742a2a" },
}

const DECISION_ICONS = {
  ALLOW: "✓", RESTRICT: "⚠", REDACT: "◉", BLOCK: "✕"
}

export default function ResultPanel({ result, loading, error }) {
  if (loading) return (
    <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "24px", border: "1px solid #2d3748", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "400px" }}>
      <div style={{ textAlign: "center", color: "#718096" }}>
        <div style={{ fontSize: "32px", marginBottom: "12px" }}>⟳</div>
        <div>Analyzing...</div>
      </div>
    </div>
  )

  if (error) return (
    <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "24px", border: "1px solid #742a2a" }}>
      <div style={{ color: "#fc8181", fontSize: "14px" }}>⚠ {error}</div>
    </div>
  )

  if (!result) return (
    <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "24px", border: "1px solid #2d3748", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "400px" }}>
      <div style={{ textAlign: "center", color: "#4a5568" }}>
        <div style={{ fontSize: "48px", marginBottom: "12px" }}>🛡️</div>
        <div style={{ fontSize: "14px" }}>Submit text to see analysis</div>
      </div>
    </div>
  )

  const colors = DECISION_COLORS[result.decision] || DECISION_COLORS.RESTRICT

  const chartData = [
    { name: "Malware", score: result.scores.malware, fill: "#fc8181" },
    { name: "Sensitive", score: result.scores.sensitive, fill: "#f6ad55" },
    { name: "Intent", score: result.scores.intent, fill: "#63b3ed" },
    { name: "Final", score: result.final_score, fill: "#667eea" },
  ]

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

      {/* Decision badge */}
      <div style={{ background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: "12px", padding: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ width: "56px", height: "56px", background: colors.badge, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "24px", color: colors.text, flexShrink: 0 }}>
          {DECISION_ICONS[result.decision]}
        </div>
        <div>
          <div style={{ fontSize: "22px", fontWeight: "700", color: colors.text }}>{result.decision}</div>
          <div style={{ fontSize: "12px", color: "#a0aec0", marginTop: "2px" }}>{result.description}</div>
          <div style={{ fontSize: "11px", color: "#718096", marginTop: "4px" }}>Final Score: {result.final_score}/10 · {result.policy} policy · {result.role} role</div>
        </div>
      </div>

      {/* Score chart */}
      <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "20px", border: "1px solid #2d3748" }}>
        <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Score Breakdown</div>
        <ResponsiveContainer width="100%" height={140}>
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: "#718096", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 10]} tick={{ fill: "#718096", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: "#2d3748", border: "none", borderRadius: "6px", color: "#e2e8f0" }} />
            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation */}
      <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "20px", border: "1px solid #2d3748" }}>
        <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Explanation</div>
        {result.explanation.map((line, i) => (
          <div key={i} style={{ fontSize: "12px", color: "#cbd5e0", padding: "6px 0", borderBottom: i < result.explanation.length - 1 ? "1px solid #2d3748" : "none", lineHeight: "1.5" }}>
            {line}
          </div>
        ))}
      </div>

      {/* Safe response */}
      <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "20px", border: "1px solid #2d3748" }}>
        <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>AI Response</div>
        <div style={{ fontSize: "13px", color: "#e2e8f0", lineHeight: "1.7" }}>{result.safe_response}</div>
      </div>

    </div>
  )
}