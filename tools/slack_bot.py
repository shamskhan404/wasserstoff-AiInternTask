import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_notification(subject, body):
    """
    Sends a Slack message with the email subject and a truncated body.
    """
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("[WARNING] Slack bot token or channel ID not configured. Skipping Slack notification.")
        return None
    try:
        truncated_body = body[:500] + "..." if len(body) > 500 else body
        message = f"*New Email Received:*\n*Subject:* {subject}\n*Body:* {truncated_body}"
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message
        )
        print("[INFO] Slack notification sent.")
        return response
    except SlackApiError as e:
        print(f"[ERROR] Slack API error: {e.response['error']}")
        return None