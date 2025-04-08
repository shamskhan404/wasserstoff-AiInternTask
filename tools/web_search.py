import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CX = os.getenv("GOOGLE_SEARCH_CX")

def search_google(query, num_results=3):
    if not API_KEY or not CX:
        print("[WARNING] Google Search API key or CX not configured. Skipping web search.")
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": num_results,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()

        search_results = []
        for item in results.get("items", []):
            search_results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", "")
            })
        return search_results
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google Search API request failed: {e}")
        return []