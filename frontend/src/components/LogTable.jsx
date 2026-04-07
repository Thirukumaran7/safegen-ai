import { useState, useEffect } from "react"
import axios from "axios"

const BACKEND_URL = "http://127.0.0.1:8000"

const DECISION_COLORS = {
  ALLOW:    "#68d391",
  RESTRICT: "#f6ad55",
  REDACT:   "#63b3ed",
  BLOCK:    "#fc8181",
}

export default function LogTable() {
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [feedbackStats, setFeedbackStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [logsRes, statsRes, feedbackRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/logs`),
        axios.get(`${BACKEND_URL}/stats`),
        axios.get(`${BACKEND_URL}/feedback-stats`)
      ])
      setLogs(logsRes.data)
      setStats(statsRes.data)
      setFeedbackStats(feedbackRes.data)
    } catch (err) {
      console.error("Failed to load logs", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div style={{ color: "#718096", textAlign: "center", padding: "40px" }}>Loading logs...</div>
  )

  return (
    <div>
      {/* Stats row */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "10px", marginBottom: "24px" }}>
          {[
            { label: "Total", value: stats.total, color: "#e2e8f0" },
            { label: "Allowed", value: stats.allowed, color: "#68d391" },
            { label: "Restricted", value: stats.restricted, color: "#f6ad55" },
            { label: "Redacted", value: stats.redacted, color: "#63b3ed" },
            { label: "Blocked", value: stats.blocked, color: "#fc8181" },
            { label: "Avg Score", value: stats.avg_score, color: "#667eea" },
            { label: "Agreement", value: feedbackStats ? `${feedbackStats.agreement_rate}%` : "N/A", color: "#68d391" },
          ].map((s, i) => (
            <div key={i} style={{ background: "#1a1d2e", borderRadius: "10px", padding: "14px", border: "1px solid #2d3748", textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: "700", color: s.color }}>{s.value}</div>
              <div style={{ fontSize: "11px", color: "#718096", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Feedback stats */}
      {feedbackStats && feedbackStats.total_feedback > 0 && (
        <div style={{ background: "#1a1d2e", borderRadius: "10px", padding: "14px 20px", border: "1px solid #2d3748", marginBottom: "16px", display: "flex", gap: "24px", alignItems: "center" }}>
          <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0" }}>Feedback Summary</div>
          <div style={{ fontSize: "12px", color: "#68d391" }}>👍 {feedbackStats.agreed_count} agreed</div>
          <div style={{ fontSize: "12px", color: "#fc8181" }}>👎 {feedbackStats.disagreed_count} disagreed</div>
          <div style={{ fontSize: "12px", color: "#667eea" }}>Agreement rate: {feedbackStats.agreement_rate}%</div>
        </div>
      )}

      {/* Logs table */}
      <div style={{ background: "#1a1d2e", borderRadius: "12px", border: "1px solid #2d3748", overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid #2d3748", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: "14px", fontWeight: "600", color: "#fff" }}>Analysis Log</div>
          <button onClick={loadData} style={{ padding: "5px 12px", background: "#2d3748", border: "none", borderRadius: "6px", color: "#e2e8f0", fontSize: "12px", cursor: "pointer" }}>Refresh</button>
        </div>

        {logs.length === 0 ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#4a5568" }}>No logs yet. Run some analyses first.</div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#0f1117" }}>
                  {["Time", "Input", "Type", "Policy", "Role", "Score", "Decision", "Threat", "Privacy", "Feedback"].map(h => (
                    <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontSize: "11px", color: "#718096", fontWeight: "500", textTransform: "uppercase", letterSpacing: "0.5px", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={i} style={{ borderTop: "1px solid #2d3748" }}>
                    <td style={{ padding: "10px 14px", fontSize: "11px", color: "#718096", whiteSpace: "nowrap" }}>
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "12px", color: "#cbd5e0", maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {log.input_text}
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "11px", color: "#718096" }}>
                      {log.input_type === "image" ? "🖼️" : log.input_type === "document" ? "📄" : "📝"}
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "12px", color: "#a0aec0" }}>{log.policy}</td>
                    <td style={{ padding: "10px 14px", fontSize: "12px", color: "#a0aec0" }}>{log.role}</td>
                    <td style={{ padding: "10px 14px", fontSize: "12px", color: "#667eea", fontWeight: "600" }}>{log.final_score}</td>
                    <td style={{ padding: "10px 14px" }}>
                      <span style={{ fontSize: "11px", fontWeight: "600", color: DECISION_COLORS[log.decision] || "#e2e8f0", background: "#0f1117", padding: "2px 8px", borderRadius: "10px" }}>
                        {log.decision}
                      </span>
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "11px", color: "#a0aec0", whiteSpace: "nowrap" }}>
                      {log.malware_type && log.malware_type !== "None" ? log.malware_type : "—"}
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "11px", color: "#a0aec0" }}>
                      {log.privacy_risk && log.privacy_risk !== "None" ? (
                        <span style={{ color: log.privacy_risk === "High" ? "#fc8181" : log.privacy_risk === "Medium" ? "#f6ad55" : "#68d391" }}>
                          {log.privacy_risk}
                        </span>
                      ) : "—"}
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "14px" }}>
                      {log.feedback_agreed === 1 ? "👍" : log.feedback_agreed === 0 ? "👎" : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}