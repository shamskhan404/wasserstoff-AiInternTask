import google.generativeai as genai
import os
import json 

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-1.5-pro-002")


def query_gemini(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("[ERROR] Gemini generation failed:", e)
        return None


def summarize_email(email_text):
    prompt = f"Summarize the following email in a few concise sentences:\n\n{email_text}"
    return query_gemini(prompt)

def detect_intent(email_text):
    prompt = f"What is the primary intent of the sender in this email? Answer in one or two words.\n\n{email_text}"
    return query_gemini(prompt)

def extract_meeting_info(email_text):
    prompt = (
        "Extract meeting details from this email. If a meeting is requested, "
        "output a JSON object with the following keys: 'summary', 'start_time' (ISO format), "
        "'end_time' (ISO format), 'location'. If no meeting is clearly requested, "
        "return an empty JSON object.\n\n"
        f"{email_text}\n\nJSON:"
    )
    response = query_gemini(prompt)
    try:
        return json.loads(response) if response else {}
    except json.JSONDecodeError:
        print(f"[ERROR] Could not decode JSON from Gemini: {response}")
        return {}

def generate_reply(email_text, context=None):
    prompt = "You are a helpful AI email assistant. Write a polite and concise reply to the following email.\n\n"
    if context:
        prompt += f"Previous messages in the thread:\n{context}\n\n"
    prompt += f"Incoming email:\n{email_text}\n\nReply:"
    return query_gemini(prompt)