# AI Email Bot

An AI-powered personal assistant that reads your Gmail inbox, understands the context of emails using Gemini (Google's LLM), and takes smart actions like replying, forwarding, searching the web, scheduling meetings, and more — all automatically.

---

## Features

-  **Gmail Integration** (via Gmail API or IMAP)
-  **LLM-based Understanding** with Gemini (free version)
  - Summarize email threads
  - Extract intent and key information
  - Generate smart replies
-  **Database Storage** with threading support
-  **Web Search Integration** for info-based email queries
-  **Slack Integration** to forward important messages
-  **Google Calendar Integration** to auto-schedule meetings
-  **Auto Replies** with approval/auto-send logic
-  **Fully Modular Codebase**
-  **AI Coding Assistant Use** (e.g., Cursor/Copilot) documented

---


## Architecture Overview

> *(You can open or edit the architecture using draw.io or diagrams.net.)*

---

### Data Flow Description

1. **Inbox Fetch**  
   Emails are fetched from Gmail via API (OAuth2).

2. **Parsing & Storage**  
   Each email’s metadata (sender, subject, body, time, etc.) is parsed and saved to a local database (SQLite/PostgreSQL).

3. **LLM Analysis (Gemini)**  
   The Gemini LLM:
   - Summarizes threads
   - Extracts intent and action items
   - Generates replies (based on templates or freestyle)

4. **Tool Integration**  
   Based on LLM outputs:
   - Events are scheduled in Google Calendar
   - Important messages are forwarded to Slack
   - Questions are resolved via web search

5. **Response Handling**  
   - Auto-send replies (if flagged safe)
   - Or log them for manual approval

---


