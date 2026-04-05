import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPTS = {
    "ALLOW": "You are a helpful AI assistant. The user's request has been reviewed and approved. Respond helpfully and completely.",
    "RESTRICT": "You are a careful AI assistant. Respond at a high level only. Do not provide specific technical details or code.",
    "REDACT": "You are a careful AI assistant. Address the general question only. Keep response brief and general.",
    "BLOCK": "You are a safety-focused AI assistant. Firmly but politely decline to help. Keep your response to 2-3 sentences maximum."
}

def generate_response(display_text, decision, policy, role, explanation):
    system_prompt = SYSTEM_PROMPTS.get(decision, SYSTEM_PROMPTS["RESTRICT"])
    full_prompt = f"{system_prompt}\n\nUser role: {role}\nPolicy level: {policy}\n\nUser message: {display_text}"
    try:
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=full_prompt)
        return {"response": response.text, "model": "gemini-2.0-flash-lite", "success": True}
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        fallback = {"ALLOW": "I am happy to help.", "RESTRICT": "I can provide general information only.", "REDACT": "I can help with the general question.", "BLOCK": "I am unable to help with this request."}
        return {"response": fallback.get(decision, "Unable to process."), "model": "fallback", "success": False, "error": str(e)}
