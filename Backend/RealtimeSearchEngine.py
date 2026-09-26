import datetime
import os
import re
from json import dump, load

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from groq import Groq

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")
BraveAPIKey = env_vars.get("BRAVE_API_KEY") or os.getenv("BRAVE_API_KEY")
SerpAPIKey = env_vars.get("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY")
SearchProvider = (env_vars.get("SEARCH_PROVIDER") or os.getenv("SEARCH_PROVIDER") or "brave").lower()


if not GroqAPIKey:
    raise ValueError(
        "GroqAPIKey was not found in your .env file."
    )


# ============================================================
# INITIALIZE GROQ
# ============================================================

client = Groq(api_key=GroqAPIKey)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

System = f"""
Hello, I am {Username}.

You are a very accurate and advanced AI chatbot named {Assistantname}.

You have access to real-time information supplied by a search engine.

Rules:
- Provide answers in a professional way.
- Use proper grammar and punctuation.
- Answer the user's question using the provided information.
- Do not claim that you searched the internet if search results were not provided.
- If the search results do not contain enough information, clearly say so.
- Do not make up information.
"""


# ============================================================
# CHAT LOG
# ============================================================

chat_log_path = os.path.join(PROJECT_ROOT, "Data", "ChatLog.json")

os.makedirs(
    os.path.dirname(chat_log_path),
    exist_ok=True
)


try:

    with open(
        chat_log_path,
        "r",
        encoding="utf-8"
    ) as f:

        messages = load(f)

        if not isinstance(messages, list):
            messages = []


except (FileNotFoundError, ValueError):

    messages = []

    with open(
        chat_log_path,
        "w",
        encoding="utf-8"
    ) as f:

        dump(
            [],
            f,
            indent=4
        )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def build_search_query(prompt):
    """Construct a fresh, current-year search query so result sets are not stale."""
    query = " ".join(str(prompt or "").strip().split())
    current_year = datetime.datetime.now().strftime("%Y")

    if not query:
        return f"latest updates {current_year}"

    year_pattern = r"\b(19\d{2}|20\d{2}|21\d{2})\b"
    if re.search(year_pattern, query):
        query = re.sub(year_pattern, current_year, query)
    elif any(keyword in query.lower() for keyword in [
        "latest", "new", "today", "recent", "breaking", "news", "update", "current"
    ]):
        query = f"{query} {current_year}"
    else:
        query = f"{query} {current_year} latest"

    return query.strip()


def BraveSearch(query):
    """Use the Brave Search API when a valid API key is configured."""
    key = BraveAPIKey or os.getenv("BRAVE_API_KEY")
    if not key:
        return None

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={
                "q": query,
                "count": 3,
                "search_lang": "en",
                "ui_lang": "en-US",
                "country": "US",
            },
            headers={
                "X-Subscription-Token": key,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("web", {}).get("results", [])

        if not results:
            return f"No live search results were found for '{query}'."

        answer = f"The live search results for '{query}' are:\n[start]\n"
        for item in results[:3]:
            title = item.get("title", "No title")
            description = item.get("description", "No description available.")
            answer += f"Title: {title}\nDescription: {description}\n\n"
        answer += "[end]"
        return answer
    except Exception as e:
        print(f"\nBrave Search Error: {e}\n")
        return None


def GoogleSearch(query):
    """Fetch fresh search results using a live API when available, else fallback to DuckDuckGo."""
    fresh_query = build_search_query(query)

    provider = SearchProvider
    if provider == "brave":
        brave_results = BraveSearch(fresh_query)
        if brave_results:
            return brave_results

    if provider == "serpapi":
        key = SerpAPIKey or os.getenv("SERPAPI_API_KEY")
        if key:
            try:
                response = requests.get(
                    "https://serpapi.com/search",
                    params={
                        "engine": "google",
                        "q": fresh_query,
                        "api_key": key,
                        "num": 3,
                    },
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()
                results = payload.get("organic_results", [])
                if results:
                    answer = f"The live search results for '{fresh_query}' are:\n[start]\n"
                    for item in results[:3]:
                        title = item.get("title", "No title")
                        description = item.get("snippet", "No description available.")
                        answer += f"Title: {title}\nDescription: {description}\n\n"
                    answer += "[end]"
                    return answer
            except Exception as e:
                print(f"\nSerpAPI Search Error: {e}\n")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        }
        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": fresh_query},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        result_blocks = soup.select(".result")

        if not result_blocks:
            return f"No live search results were found for '{fresh_query}'."

        answer = f"The live search results for '{fresh_query}' are:\n[start]\n"

        for result in result_blocks[:3]:
            title_tag = result.select_one("a.result-link")
            snippet_tag = result.select_one(".result__snippet")

            title = title_tag.get_text(" ", strip=True) if title_tag else "No title"
            description = snippet_tag.get_text(" ", strip=True) if snippet_tag else "No description available."
            answer += f"Title: {title}\nDescription: {description}\n\n"

        answer += "[end]"
        return answer

    except Exception as e:
        print(f"\nLive Search Error: {e}\n")
        return f"Live search could not be completed for '{fresh_query}'."


# ============================================================
# ANSWER MODIFIER
# ============================================================

def AnswerModifier(answer):

    lines = answer.split("\n")

    non_empty_lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    return "\n".join(non_empty_lines)


# ============================================================
# REAL-TIME INFORMATION
# ============================================================

def Information():

    current_date_time = datetime.datetime.now()

    return f"""
Current real-time information:

Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d %B %Y")}
Time: {current_date_time.strftime("%H:%M:%S")}
"""


# ============================================================
# REAL-TIME SEARCH ENGINE
# ============================================================

def RealtimeSearchEngine(prompt):

    global messages


    # --------------------------------------------------------
    # Reload chat history
    # --------------------------------------------------------

    try:

        with open(
            chat_log_path,
            "r",
            encoding="utf-8"
        ) as f:

            messages = load(f)

            if not isinstance(messages, list):
                messages = []


    except (FileNotFoundError, ValueError):

        messages = []


    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # --------------------------------------------------------
    # Limit history
    # --------------------------------------------------------

    MAX_MESSAGES = 3

    if len(messages) > MAX_MESSAGES:

        messages = messages[-MAX_MESSAGES:]


    # --------------------------------------------------------
    # Google Search
    # --------------------------------------------------------

    search_query = build_search_query(prompt)
    search_results = GoogleSearch(search_query)


    # --------------------------------------------------------
    # Prepare messages
    # --------------------------------------------------------

    chat_messages = [

        {
            "role": "system",
            "content": System
        },

        {
            "role": "system",
            "content": Information()
        },

        {
            "role": "system",
            "content": search_results
        }

    ] + messages


    # --------------------------------------------------------
    # Groq Request
    # --------------------------------------------------------

    try:

        completion = client.chat.completions.create(
            model=MODEL,
            messages=chat_messages,
            temperature=0.5,
            max_tokens=1024,
            top_p=0.9,
            stream=False
        )

        # ----------------------------------------------------
        # Collect response
        # ----------------------------------------------------
        Answer = completion.choices[0].message.content or ""
        if not Answer and getattr(completion.choices[0].message, "reasoning", None):
            Answer = completion.choices[0].message.reasoning

        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": Answer
            }
        )


        with open(
            chat_log_path,
            "w",
            encoding="utf-8"
        ) as f:

            dump(
                messages,
                f,
                indent=4,
                ensure_ascii=False
            )


        return AnswerModifier(Answer)


    except Exception as e:

        print(
            f"\nGroq Error: {e}\n"
        )

        return (
            "Sorry, there was an issue processing "
            "your request. Please try again."
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        f"{Assistantname} Real-Time Search Engine Started."
    )

    print(
        "Type 'exit' or 'quit' to stop.\n"
    )


    while True:

        prompt = input(
            "ENTER YOUR QUERY: "
        ).strip()


        if not prompt:

            continue


        if prompt.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print(
                f"Goodbye, {Username}! 👋"
            )

            break


        print(
            "\n" +
            RealtimeSearchEngine(prompt) +
            "\n"
        )
