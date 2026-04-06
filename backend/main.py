from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

from agents.risk_analyzer import run_risk_analysis
from agents.response_controller import generate_response
from database.logger import init_db, log_analysis, get_logs, get_stats

load_dotenv()

app = FastAPI(title="SafeGen AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    print("SafeGen AI backend started")
    print("Database initialized")
    # Train model if not exists
    import os
    model_path = os.path.join("ml", "intent_model.pkl")
    if not os.path.exists(model_path):
        print("Model not found. Training now...")
        import subprocess
        subprocess.run(["python", "ml/train_model.py"], check=True)
        print("Model trained successfully")

# Request model
class AnalyzeRequest(BaseModel):
    text: str
    policy: Literal["strict", "moderate", "open"] = "moderate"
    role: Literal["student", "general", "expert"] = "general"

# Main analyze endpoint
@app.post("/analyze")
async def analyze(request: AnalyzeRequest):

    # Run Agent 1 — Risk Analysis
    analysis = run_risk_analysis(
        text   = request.text,
        policy = request.policy,
        role   = request.role
    )

    # Run Agent 2 — Generate safe response
    response = generate_response(
        display_text = analysis["display_text"],
        decision     = analysis["decision"]["decision"],
        policy       = request.policy,
        role         = request.role,
        explanation  = analysis["explanation"]
    )

    # Log to database
    log_analysis(analysis)

    # Return full result
    return {
        "decision":      analysis["decision"]["decision"],
        "description":   analysis["decision"]["description"],
        "reason":        analysis["decision"]["reason"],
        "final_score":   analysis["scoring"]["final_score"],
        "scores": {
            "malware":   analysis["malware"]["score"],
            "sensitive": analysis["sensitive"]["score"],
            "intent":    analysis["intent"]["score"],
        },
        "contributions": analysis["scoring"]["contributions"],
        "flags":         analysis["malware"]["flags"],
        "sensitive_types_found": analysis["sensitive"]["types_found"],
        "intent_label":  analysis["intent"]["label"],
        "injection_detected": analysis["intent"]["injection_detected"],
        "injection_patterns": analysis["intent"]["injection_patterns"],
        "explanation":   analysis["explanation"],
        "safe_response": response["response"],
        "display_text":  analysis["display_text"],
        "policy":        request.policy,
        "role":          request.role,
    }

@app.get("/logs")
async def logs(limit: int = 50):
    return get_logs(limit)

@app.get("/stats")
async def stats():
    return get_stats()

@app.get("/health")
async def health():
    return {"status": "ok", "message": "SafeGen AI is running"}