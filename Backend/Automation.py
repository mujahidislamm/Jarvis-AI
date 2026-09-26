from urllib.parse import quote_plus

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
os.makedirs(DATA_DIR, exist_ok=True)

# Load environment variables
env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
GroqAPIKey = env_vars.get("GroqAPIKey")

# Groq API Client
client = Groq(api_key=GroqAPIKey)

# List of professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need. Don't hesitate to ask."
]

# System Chatbot Messages
messages = []
SystemChatbot = [{"role": "system", "content": f"Hello, I am {os.getenv('Username', 'Assistant')}, your content writer. Write content like a letter."}]

# Google Search Function
def GoogleSearch(Topic):
    search(Topic)
    return True

# AI Content Writing Function
def content(Topic):
    def OpenNotepad(File):
        subprocess.run(["notepad.exe", File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=SystemChatbot + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True
        )
        
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("content ", "")
    ContentByAI = ContentWriterAI(Topic)
    
    file_path = os.path.join(DATA_DIR, f"{Topic.lower().replace(' ', '')}.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(file_path)
    return True

# YouTube Search Function
def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

# Play YouTube Video
def PlayYoutube(query):
    playonyt(query)
    return True

POPULAR_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "google photos": "https://photos.google.com/",
    "photos": "https://photos.google.com/",
    "google drive": "https://drive.google.com/",
    "drive": "https://drive.google.com/",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chatgpt.com",
    "openai": "https://openai.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "whatsapp": "https://web.whatsapp.com",
    "amazon": "https://www.amazon.com",
    "linkedin": "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "twitch": "https://www.twitch.tv",
    "discord": "https://discord.com/app",
    "pinterest": "https://www.pinterest.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
}

PLATFORM_SEARCH_URLS = {
    "google": "https://www.google.com/search?q={query}",
    "facebook": "https://www.facebook.com/search/top/?q={query}",
    "instagram": "https://www.instagram.com/explore/search/keyword/?q={query}",
    "twitter": "https://x.com/search?q={query}",
    "x": "https://x.com/search?q={query}",
    "github": "https://github.com/search?q={query}&type=repositories",
    "reddit": "https://www.reddit.com/search/?q={query}",
    "amazon": "https://www.amazon.com/s?k={query}",
    "linkedin": "https://www.linkedin.com/search/results/all/?keywords={query}",
    "wikipedia": "https://en.wikipedia.org/w/index.php?search={query}",
    "spotify": "https://open.spotify.com/search/{query}",
    "netflix": "https://www.netflix.com/search?q={query}",
    "maps": "https://www.google.com/maps/search/?api=1&query={query}",
    "gmail": "https://mail.google.com/mail/u/0/#search/{query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
}

COMMON_WINDOWS_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "ms-settings:",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "msedge": "msedge.exe",
}

def PlatformSearch(platform, query):
    platform = platform.strip().lower().replace(" ", "")
    platform = "x" if platform == "twitter" else platform
    url = PLATFORM_SEARCH_URLS.get(platform)
    if not url or not query:
        return False
    search_query = quote_plus(query.strip())
    destination = url.format(query=search_query)
    webbrowser.open(destination)
    return True


# Open Applications & Websites
def OpenApp(app, sess=requests.session()):
    app_clean = app.strip().lower()
    app_clean = app_clean.removeprefix("the ").strip()

    # 1. Known websites should always win over installed desktop apps.
    if app_clean in POPULAR_WEBSITES:
        webbrowser.open(POPULAR_WEBSITES[app_clean])
        return True

    # 2. Special-case YouTube commands that should play directly instead of searching.
    if "youtube" in app_clean:
        if "and play" in app_clean:
            query = app_clean.split("and play", 1)[1].strip()
            query = query.replace(" on youtube", "").strip()
            if query:
                PlayYoutube(query)
                return True
        if "play" in app_clean and app_clean.startswith("youtube"):
            query = app_clean.replace("youtube", "", 1).replace("play", "", 1).strip()
            query = query.replace(" on youtube", "").strip()
            if query:
                PlayYoutube(query)
                return True

    # 3. Generic platform search: "google shoes", "facebook my page", "instagram travel"
    known_platforms = sorted(PLATFORM_SEARCH_URLS.keys(), key=len, reverse=True)
    for platform in known_platforms:
        if app_clean.startswith(platform + " "):
            query = app_clean[len(platform):].strip()
            if query:
                return PlatformSearch(platform, query)

        if " on " + platform in app_clean:
            query = app_clean.split(f" on {platform}", 1)[0].strip()
            if query and any(word in query for word in ["search", "find", "open", "look for", "for"]):
                query = query.replace("search", "").replace("find", "").replace("open", "").replace("look for", "").replace("for", "").strip()
            if query:
                return PlatformSearch(platform, query)

    # 4. Special-case YouTube so a user query opens a YouTube search, not the homepage.
    if app_clean == "youtube":
        webbrowser.open("https://www.youtube.com")
        return True

    if app_clean.startswith("youtube "):
        query = app_clean[len("youtube "):].strip()
        if query:
            search_query = quote_plus(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            return True
        webbrowser.open("https://www.youtube.com")
        return True

    if app_clean.startswith("youtube search "):
        query = app_clean[len("youtube search "):].strip()
        if query:
            search_query = quote_plus(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            return True
        webbrowser.open("https://www.youtube.com")
        return True

    # 2. Check direct URL patterns
    if app_clean.startswith(("http://", "https://")):
        webbrowser.open(app_clean)
        return True
    if any(app_clean.endswith(tld) for tld in [".com", ".org", ".net", ".io", ".in", ".co", ".ai", ".tv", ".app", ".dev"]) and " " not in app_clean:
        webbrowser.open(f"https://{app_clean}")
        return True

    # 3. Check known Windows built-in apps
    if app_clean in COMMON_WINDOWS_APPS:
        target = COMMON_WINDOWS_APPS[app_clean]
        try:
            if target.endswith(":"):
                os.system(f"start {target}")
            else:
                subprocess.Popen(target, shell=True)
            return True
        except Exception:
            pass

    # 4. Try AppOpener for installed desktop apps
    try:
        appopen(app_clean, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        pass

    # 5. Try Windows start command
    try:
        subprocess.Popen(f"start {app_clean}", shell=True)
        return True
    except Exception:
        pass

    # 6. Fallback to Google search
    webbrowser.open(f"https://www.google.com/search?q={app_clean}")
    return True

# Close Applications
def CloseApp(app):
    app_clean = app.strip().lower()
    if app_clean in COMMON_WINDOWS_APPS:
        target = COMMON_WINDOWS_APPS[app_clean]
        if target.endswith(".exe"):
            os.system(f"taskkill /f /im {target} >nul 2>&1")
            return True
    try:
        if "chrome" not in app_clean:
            close(app_clean, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False

# System Controls
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    if command in actions:
        actions[command]()
    return True

# Execute Commands Asynchronously
async def TranslateAndExecute(commands: list[str]):
    tasks = []
    
    for command in commands:
        if command.startswith("open"):
            tasks.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close"):
            tasks.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play"):
            tasks.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content"):
            tasks.append(asyncio.to_thread(content, command.removeprefix("content ")))
        elif command.startswith("google search"):
            tasks.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search"):
            tasks.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system"):
            tasks.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print(f"No function found for: {command}")
    
    results = await asyncio.gather(*tasks)
    return results

# Main Automation Execution
async def Automation(commands: list[str]):
    await TranslateAndExecute(commands)
    return True


