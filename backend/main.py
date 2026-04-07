from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
from dotenv import load_dotenv

from agents.risk_analyzer import run_risk_analysis, analyze_image, analyze_document
from agents.response_controller import generate_response
from database.logger import init_db, log_analysis, log_feedback, get_logs, get_stats, get_feedback_stats

load_dotenv()

app = FastAPI(title="SafeGen AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    print("SafeGen AI v2 backend started")
    print("Database initialized")
    import os
    model_path = os.path.join("ml", "intent_model.pkl")
    if not os.path.exists(model_path):
        print("Model not found. Training now...")
        import subprocess
        subprocess.run(["python", "ml/train_model.py"], check=True)
        print("Model trained successfully")

class AnalyzeRequest(BaseModel):
    text: str
    policy: Literal["strict", "moderate", "open"] = "moderate"
    role: Literal["student", "general", "expert"] = "general"

class ImageAnalyzeRequest(BaseModel):
    image_base64: str
    policy: Literal["strict", "moderate", "open"] = "moderate"
    role: Literal["student", "general", "expert"] = "general"

class DocumentAnalyzeRequest(BaseModel):
    content: str
    filename: Optional[str] = "document"
    policy: Literal["strict", "moderate", "open"] = "moderate"
    role: Literal["student", "general", "expert"] = "general"

class FeedbackRequest(BaseModel):
    log_id: int
    agreed: bool
    suggested_decision: Optional[str] = None
    user_comment: Optional[str] = None

def format_analysis_response(analysis: dict, response_text: str, log_id, policy: str, role: str, input_type: str = "text", filename: str = None) -> dict:
    result = {
        "log_id":              log_id,
        "decision":            analysis["decision"]["decision"],
        "description":         analysis["decision"]["description"],
        "reason":              analysis["decision"]["reason"],
        "final_score":         analysis["scoring"]["final_score"],
        "scores": {
            "malware":         analysis["malware"]["score"],
            "sensitive":       analysis["sensitive"]["score"],
            "intent":          analysis["intent"]["score"],
        },
        "contributions":       analysis["scoring"]["contributions"],
        "malware_type":        analysis["malware"]["malware_type"],
        "malware_category":    analysis["malware"]["malware_category"],
        "severity":            analysis["malware"]["severity"],
        "malware_description": analysis["malware"]["description"],
        "flags":               analysis["malware"]["flags"],
        "sensitive_types_found": analysis["sensitive"]["types_found"],
        "anonymisation_score": analysis["sensitive"]["anonymisation_score"],
        "pii_count":           analysis["sensitive"]["pii_count"],
        "privacy_risk":        analysis["sensitive"]["privacy_risk"],
        "pii_summary":         analysis["sensitive"]["pii_summary"],
        "intent_label":        analysis["intent"]["label"],
        "threat_category":     analysis["intent"]["threat_category"],
        "injection_detected":  analysis["intent"]["injection_detected"],
        "injection_patterns":  analysis["intent"]["injection_patterns"],
        "explanation":         analysis["explanation"],
        "safe_response":       response_text,
        "display_text":        analysis["display_text"],
        "policy":              policy,
        "role":                role,
        "input_type":          input_type,
    }
    if filename:
        result["filename"] = filename
    return result

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    analysis = run_risk_analysis(
        text=request.text,
        policy=request.policy,
        role=request.role
    )
    response = generate_response(
        display_text=analysis["display_text"],
        decision=analysis["decision"]["decision"],
        policy=request.policy,
        role=request.role,
        explanation=analysis["explanation"]
    )
    log_id = log_analysis(analysis, input_type="text")
    return format_analysis_response(analysis, response["response"], log_id, request.policy, request.role, "text")

@app.post("/analyze-image")
async def analyze_image_endpoint(request: ImageAnalyzeRequest):
    result = analyze_image(
        image_base64=request.image_base64,
        policy=request.policy,
        role=request.role
    )
    return result

@app.post("/analyze-document")
async def analyze_document_endpoint(request: DocumentAnalyzeRequest):
    analysis = analyze_document(
        content=request.content,
        filename=request.filename,
        policy=request.policy,
        role=request.role
    )
    response = generate_response(
        display_text=analysis["display_text"],
        decision=analysis["decision"]["decision"],
        policy=request.policy,
        role=request.role,
        explanation=analysis["explanation"]
    )
    log_id = log_analysis(analysis, input_type="document")
    return format_analysis_response(analysis, response["response"], log_id, request.policy, request.role, "document", request.filename)

@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    success = log_feedback(
        log_id=request.log_id,
        agreed=request.agreed,
        suggested_decision=request.suggested_decision,
        user_comment=request.user_comment
    )
    return {"success": success, "message": "Feedback recorded" if success else "Failed to record feedback"}

@app.get("/logs")
async def logs(limit: int = 50):
    return get_logs(limit)

@app.get("/stats")
async def stats():
    return get_stats()

@app.get("/feedback-stats")
async def feedback_stats():
    return get_feedback_stats()

@app.get("/health")
async def health():
    return {"status": "ok", "message": "SafeGen AI v2 is running", "version": "2.0.0"}