import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPTS = {
    "ALLOW": """You are a helpful AI assistant. The user's request has been reviewed and approved as safe.
Respond helpfully, clearly, and completely to the user's question.""",

    "RESTRICT": """You are a careful AI assistant. The user's request has been flagged as potentially risky.
You must respond at a HIGH LEVEL ONLY — no technical details, no code, no step-by-step instructions.
Acknowledge the topic briefly and explain why detailed guidance cannot be provided.
Keep your response to 3-4 sentences maximum.""",

    "REDACT": """You are a careful AI assistant. Sensitive data was detected in this request and has been masked.
Address the general topic only — do not reference or repeat any personal data.
Keep your response brief, general, and cautious.
Remind the user not to share sensitive information with AI systems.""",

    "BLOCK": """You are a safety-focused AI assistant. This request has been blocked because it violates safety policy.
Firmly but politely decline to help. Do not provide any information related to the request.
Explain briefly that this type of request cannot be assisted with.
Keep your response to 2-3 sentences maximum."""
}

def generate_response(display_text, decision, policy, role, explanation):
    system_prompt = SYSTEM_PROMPTS.get(decision, SYSTEM_PROMPTS["RESTRICT"])

    full_prompt = f"""{system_prompt}

User role: {role}
Policy level: {policy}
Safety decision: {decision}

User message: {display_text}

Respond appropriately based on the safety decision above."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return {
            "response": response.text,
            "model": "gemini-2.5-flash",
            "success": True
        }
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        fallback = {
            "ALLOW":    "I am happy to help with your question. Please feel free to ask for more details.",
            "RESTRICT": "I can only provide general information on this topic. Detailed technical guidance cannot be provided as this request has been flagged by the safety system.",
            "REDACT":   "Sensitive data was detected in your message and has been masked. Please avoid sharing personal or sensitive information with AI systems.",
            "BLOCK":    "This request has been blocked by the safety system as it violates our usage policy. I am unable to assist with this type of request."
        }
        return {
            "response": fallback.get(decision, "Unable to process this request."),
            "model": "fallback",
            "success": False,
            "error": str(e)
        }