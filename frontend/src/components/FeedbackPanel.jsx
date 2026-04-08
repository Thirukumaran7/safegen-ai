import { useState } from "react"
import axios from "axios"

const BACKEND_URL = "https://safegen-ai-backend.onrender.com"

export default function FeedbackPanel({ logId, currentDecision }) {
  const [submitted, setSubmitted] = useState(false)
  const [agreed, setAgreed] = useState(null)
  const [suggested, setSuggested] = useState("")
  const [comment, setComment] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (agreeValue) => {
    setLoading(true)
    setAgreed(agreeValue)
    try {
      await axios.post(`${BACKEND_URL}/feedback`, {
        log_id: logId,
        agreed: agreeValue,
        suggested_decision: agreeValue ? null : suggested || null,
        user_comment: comment || null
      })
      setSubmitted(true)
    } catch (err) {
      console.error("Feedback error:", err)
      setSubmitted(true)
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "16px 20px", border: "1px solid #2d3748", textAlign: "center" }}>
        <div style={{ fontSize: "20px", marginBottom: "6px" }}>
          {agreed ? "👍" : "👎"}
        </div>
        <div style={{ fontSize: "13px", color: "#68d391", fontWeight: "600" }}>
          Feedback recorded
        </div>
        <div style={{ fontSize: "11px", color: "#718096", marginTop: "4px" }}>
          Thank you — this helps improve the system
        </div>
      </div>
    )
  }

  return (
    <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "16px 20px", border: "1px solid #2d3748" }}>
      <div style={{ fontSize: "13px", fontWeight: "600", color: "#a0aec0", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        Was this decision correct?
      </div>

      {/* Thumbs up / down */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "12px" }}>
        <button
          onClick={() => handleSubmit(true)}
          disabled={loading}
          style={{ flex: 1, padding: "10px", background: "#0d2b1a", border: "1px solid #22543d", borderRadius: "8px", color: "#68d391", fontSize: "16px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}
        >
          👍 <span style={{ fontSize: "13px" }}>Correct</span>
        </button>
        <button
          onClick={() => setAgreed(false)}
          disabled={loading}
          style={{ flex: 1, padding: "10px", background: agreed === false ? "#2d0f0f" : "#1a1d2e", border: `1px solid ${agreed === false ? "#742a2a" : "#2d3748"}`, borderRadius: "8px", color: "#fc8181", fontSize: "16px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}
        >
          👎 <span style={{ fontSize: "13px" }}>Incorrect</span>
        </button>
      </div>

      {/* Show extra options when disagreed */}
      {agreed === false && (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div>
            <div style={{ fontSize: "11px", color: "#718096", marginBottom: "4px" }}>What should the decision be?</div>
            <select
              value={suggested}
              onChange={e => setSuggested(e.target.value)}
              style={{ width: "100%", background: "#2d3748", color: "#e2e8f0", border: "1px solid #4a5568", borderRadius: "6px", padding: "6px 10px", fontSize: "12px" }}
            >
              <option value="">Select correct decision</option>
              <option value="ALLOW">ALLOW</option>
              <option value="RESTRICT">RESTRICT</option>
              <option value="REDACT">REDACT</option>
              <option value="BLOCK">BLOCK</option>
            </select>
          </div>
          <div>
            <div style={{ fontSize: "11px", color: "#718096", marginBottom: "4px" }}>Optional comment</div>
            <input
              value={comment}
              onChange={e => setComment(e.target.value)}
              placeholder="Why was this decision wrong?"
              style={{ width: "100%", background: "#2d3748", color: "#e2e8f0", border: "1px solid #4a5568", borderRadius: "6px", padding: "6px 10px", fontSize: "12px", boxSizing: "border-box" }}
            />
          </div>
          <button
            onClick={() => handleSubmit(false)}
            disabled={loading}
            style={{ padding: "8px", background: "linear-gradient(135deg, #667eea, #764ba2)", border: "none", borderRadius: "6px", color: "#fff", fontSize: "13px", fontWeight: "600", cursor: "pointer" }}
          >
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  )
}