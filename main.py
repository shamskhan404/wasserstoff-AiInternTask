import time
import os
import re

from utils.email_parser import fetch_and_store_emails
from llm.reply_generator import generate_reply, detect_meeting_request
from llm.gemini_handler import summarize_email, detect_intent, extract_meeting_info
from tools.web_search import search_google
from database.db_handler import get_latest_unprocessed_email, mark_email_as_processed
from tools.calendar_bot import create_calendar_event, create_dummy_calendar_event
from tools.slack_bot import send_slack_notification
from tools.gmail_handler import send_reply

# Configuration for auto-reply safeguards
AUTO_REPLY_ENABLED = True
SIMPLE_REPLY_INTENTS = ["acknowledgement", "thanks", "greetings"]

# Allowed senders (for security)
ALLOWED_SENDERS = {"sam77extra@gmail.com", "saraswatvimal1@gmail.com","yousufabeimam@gmail.com","arun44singh44@gmail.com","merajalam90389@gmail.com"}

# Memory cache to avoid reprocessing emails within one runtime
processed_ids = set()

def extract_email_address(sender_field):
    match = re.search(r'<(.+?)>', sender_field)
    return match.group(1) if match else sender_field.strip()

def main():
    print("Email Assistant Started.")
    while True:
        # Fetch latest emails during each loop
        try:
            fetch_and_store_emails()
        except Exception as e:
            print(f"[ERROR] Failed to fetch emails: {e}")

        email = get_latest_unprocessed_email()

        if email and email['id'] not in processed_ids:
            print(f"\nNew email from: {email['sender']} | Subject: {email['subject']}")
            processed_ids.add(email['id'])
            sender_email = extract_email_address(email['sender'])
            if sender_email not in ALLOWED_SENDERS:
                print(f"Sender '{sender_email}' not allowed. Skipping...")
                mark_email_as_processed(email['id'])
                continue
            try:
                intent = detect_intent(email['body'])
            except Exception as e:
                print(f"[ERROR] Intent detection failed: {e}")
                intent = None
            print(f"Detected intent: {intent if intent else 'None'}")
            try:
                email_summary = summarize_email(email['body'])
                print(f"Summary: {email_summary}")
            except Exception as e:
                print(f"[ERROR] Summary generation failed: {e}")
                email_summary = "Summary not available."
            reply = None
            try:
                if detect_meeting_request(email['body']):
                    print("Meeting request detected.")
                    meeting_details = extract_meeting_info(email['body'])
                    print(f"Extracted details: {meeting_details}")
                    calendar_link = (
                        create_calendar_event(meeting_details)
                        if os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
                        else create_dummy_calendar_event(meeting_details)
                    )
                    reply = generate_reply(email['body'], intent='schedule_meeting', context=str(meeting_details))
                elif intent and 'question' in intent.lower():
                    print("Question detected. Performing web search...")
                    search_results = search_google(email['body'])
                    reply_context = "\n".join([f"[{r['title']}]({r['link']})\n{r['snippet']}" for r in search_results])
                    reply = generate_reply(email['body'], intent='answer_question', context=reply_context)
                else:
                    reply = generate_reply(email['body'], intent=intent)
            except Exception as e:
                print(f"[ERROR] Reply generation failed: {e}")
                reply = None
            if reply:
                if AUTO_REPLY_ENABLED or (intent and intent.lower() in SIMPLE_REPLY_INTENTS):
                    try:
                        send_reply(email['sender'], email['subject'], reply)
                        print("Reply sent.")
                    except Exception as e:
                        print(f"[ERROR] Failed to send email: {e}")
                else:
                    print(f"Reply requires review for intent: {intent}")
                    print(f"Generated reply: {reply}")
            else:
                print("Empty reply generated. Skipping send.")
            try:
                send_slack_notification(
                    email['subject'],
                    f"Summary: {email_summary}\n\nBody: {email['body']}"
                )
            except Exception:
                print(f"[WARNING] Slack bot config missing. Skipping Slack notification.")

            mark_email_as_processed(email['id'])
            print("Marked email as processed.")

        else:
            print("No new emails. Sleeping...")
        time.sleep(10)

if __name__ == '__main__':
    main()
