import { useState, useEffect } from "react"
import axios from "axios"

const DECISION_COLORS = {
  ALLOW:    "#68d391",
  RESTRICT: "#f6ad55",
  REDACT:   "#63b3ed",
  BLOCK:    "#fc8181",
}

export default function LogTable() {
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([
        axios.get("https://safegen-ai-backend.onrender.com/logs"),
        axios.get("https://safegen-ai-backend.onrender.com/stats")
      ])
      setLogs(logsRes.data)
      setStats(statsRes.data)
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
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: "12px", marginBottom: "24px" }}>
          {[
            { label: "Total", value: stats.total, color: "#e2e8f0" },
            { label: "Allowed", value: stats.allowed, color: "#68d391" },
            { label: "Restricted", value: stats.restricted, color: "#f6ad55" },
            { label: "Redacted", value: stats.redacted, color: "#63b3ed" },
            { label: "Blocked", value: stats.blocked, color: "#fc8181" },
            { label: "Avg Score", value: stats.avg_score, color: "#667eea" },
          ].map((s, i) => (
            <div key={i} style={{ background: "#1a1d2e", borderRadius: "10px", padding: "16px", border: "1px solid #2d3748", textAlign: "center" }}>
              <div style={{ fontSize: "22px", fontWeight: "700", color: s.color }}>{s.value}</div>
              <div style={{ fontSize: "11px", color: "#718096", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
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
                  {["Time", "Input", "Policy", "Role", "Score", "Decision", "Intent"].map(h => (
                    <th key={h} style={{ padding: "10px 16px", textAlign: "left", fontSize: "11px", color: "#718096", fontWeight: "500", textTransform: "uppercase", letterSpacing: "0.5px", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={i} style={{ borderTop: "1px solid #2d3748" }}>
                    <td style={{ padding: "10px 16px", fontSize: "11px", color: "#718096", whiteSpace: "nowrap" }}>
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: "12px", color: "#cbd5e0", maxWidth: "200px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {log.input_text}
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: "12px", color: "#a0aec0" }}>{log.policy}</td>
                    <td style={{ padding: "10px 16px", fontSize: "12px", color: "#a0aec0" }}>{log.role}</td>
                    <td style={{ padding: "10px 16px", fontSize: "12px", color: "#667eea", fontWeight: "600" }}>{log.final_score}</td>
                    <td style={{ padding: "10px 16px" }}>
                      <span style={{ fontSize: "11px", fontWeight: "600", color: DECISION_COLORS[log.decision] || "#e2e8f0", background: "#0f1117", padding: "2px 8px", borderRadius: "10px" }}>
                        {log.decision}
                      </span>
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: "12px", color: "#a0aec0" }}>{log.intent_label}</td>
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