import { useState } from "react"
import axios from "axios"
import InputPanel from "./components/InputPanel"
import ResultPanel from "./components/ResultPanel"
import LogTable from "./components/LogTable"

const BACKEND_URL = "http://127.0.0.1:8000"

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState("analyze")

  const handleAnalyze = async (text, policy, role) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await axios.post(`${BACKEND_URL}/analyze`, {
        text, policy, role
      })
      setResult(response.data)
    } catch (err) {
      setError("Backend error. Make sure the FastAPI server is running.")
    } finally {
      setLoading(false)
    }
  }

  const handleImageAnalyze = async (imageBase64, policy, role) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await axios.post(`${BACKEND_URL}/analyze-image`, {
        image_base64: imageBase64, policy, role
      })
      setResult({ ...response.data, isImageResult: true })
    } catch (err) {
      setError("Image analysis failed. Make sure the backend is running.")
    } finally {
      setLoading(false)
    }
  }

  const handleDocumentAnalyze = async (content, filename, policy, role) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await axios.post(`${BACKEND_URL}/analyze-document`, {
        content, filename, policy, role
      })
      setResult(response.data)
    } catch (err) {
      setError("Document analysis failed. Make sure the backend is running.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#e2e8f0", fontFamily: "system-ui, sans-serif" }}>

      {/* Header */}
      <div style={{ background: "#1a1d2e", borderBottom: "1px solid #2d3748", padding: "16px 32px", display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{ width: "32px", height: "32px", background: "linear-gradient(135deg, #667eea, #764ba2)", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px" }}>🛡️</div>
        <div>
          <div style={{ fontSize: "18px", fontWeight: "700", color: "#fff" }}>SafeGen AI</div>
          <div style={{ fontSize: "11px", color: "#718096" }}>Adaptive Guardrail System v2</div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
          <button onClick={() => setActiveTab("analyze")} style={{ padding: "6px 16px", borderRadius: "6px", border: "none", cursor: "pointer", background: activeTab === "analyze" ? "#667eea" : "#2d3748", color: "#fff", fontSize: "13px" }}>Analyze</button>
          <button onClick={() => setActiveTab("logs")} style={{ padding: "6px 16px", borderRadius: "6px", border: "none", cursor: "pointer", background: activeTab === "logs" ? "#667eea" : "#2d3748", color: "#fff", fontSize: "13px" }}>Logs</button>
        </div>
      </div>

      {/* Main content */}
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "32px 24px" }}>
        {activeTab === "analyze" ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
            <InputPanel
              onAnalyze={handleAnalyze}
              onImageAnalyze={handleImageAnalyze}
              onDocumentAnalyze={handleDocumentAnalyze}
              loading={loading}
            />
            <ResultPanel result={result} loading={loading} error={error} />
          </div>
        ) : (
          <LogTable />
        )}
      </div>
    </div>
  )
}