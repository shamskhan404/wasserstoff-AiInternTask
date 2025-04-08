import os
import google.generativeai as genai
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def trim_email_body(body, max_tokens=2048):
    """
    Trims the email body to stay within token limits (~4 chars/token).
    """
    max_chars = max_tokens * 4
    return body[:max_chars]


def generate_reply(email_body, intent=None, context=None, conversation_history=None):
    """
    Generate a concise professional reply to an email using Gemini.
    """
    trimmed_body = trim_email_body(email_body)
    
    prompt = (
        "You are a helpful AI email assistant. Read the email below and respond professionally "
        "and concisely in 80-120 words.\n\n"
        f"Email:\n{trimmed_body}\n"
    )

    if intent == 'schedule_meeting':
        prompt += "\nThe sender is requesting to schedule a meeting. If specific times were proposed, acknowledge them. If not, suggest your availability or ask for their preferred times and duration.\n"
        if context:
            try:
                meeting_details = json.loads(context)
                prompt += (
                    f"Meeting details extracted:\n"
                    f"Summary: {meeting_details.get('summary', 'N/A')}\n"
                    f"Start Time: {meeting_details.get('start_time', 'N/A')}\n"
                    f"End Time: {meeting_details.get('end_time', 'N/A')}\n"
                    f"Location: {meeting_details.get('location', 'N/A')}\n"
                )
            except json.JSONDecodeError:
                prompt += "Could not parse meeting details.\n"

    elif intent == 'answer_question':
        prompt += "\nThe sender has asked a question. If you have relevant information from web search (provided in the context), use it to answer concisely.\n"
        if context:
            prompt += f"\nWeb search results:\n{context}\n"

    elif intent == 'forward_info':
        prompt += "\nThe sender wants information forwarded. Acknowledge that you will forward the information.\n"

    if conversation_history:
        prompt += f"\nConversation history:\n{conversation_history}\n"

    prompt += "\nReply:"

    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate reply: {e}")
        return None


def detect_meeting_request(email_text: str) -> bool:
    """
    Detects if an email is requesting to schedule a meeting using keyword search.
    """
    keywords = ["meeting", "schedule", "appointment", "call", "catch up", "sync", "let's meet", "calendar"]
    return any(word in email_text.lower() for word in keywords)
