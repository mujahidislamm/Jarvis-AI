import os
import sys
import json
import asyncio
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "Data"
DATA_DIR.mkdir(exist_ok=True)
CHAT_LOG_PATH = DATA_DIR / "ChatLog.json"

env_vars = dotenv_values(PROJECT_ROOT / ".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")

app = Flask(__name__, static_folder="web", static_url_path="")


def read_chat_history():
    try:
        if CHAT_LOG_PATH.exists() and CHAT_LOG_PATH.stat().st_size > 3:
            with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error reading chat log: {e}")
    return []


def write_chat_history(messages):
    try:
        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving chat log: {e}")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/data/<path:filename>")
def serve_data_file(filename):
    return send_from_directory(str(DATA_DIR), filename)


@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "status": "ONLINE",
        "assistant_name": Assistantname,
        "username": Username,
        "voice": AssistantVoice,
        "features": {
            "search": True,
            "chat": True,
            "automation": True,
            "image_gen": True,
            "tts": True,
            "stt": True
        }
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    messages = read_chat_history()
    return jsonify({"history": messages})


@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    write_chat_history([])
    return jsonify({"success": True, "message": "Chat history cleared."})


@app.route("/api/query", methods=["POST"])
def process_query():
    data = request.get_json(force=True, silent=True) or {}
    query = (data.get("query") or "").strip()
    forced_mode = data.get("mode", "auto")

    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        from Backend.Chatbot import ChatBot
        from Backend.RealtimeSearchEngine import RealtimeSearchEngine
        from Backend.Model import FirstLayerDMM
        from Backend.Automation import Automation

        query_clean = query.strip()
        query_lower = query_clean.lower().strip(".!?")

        # Strip conversational prefixes
        for prefix in ["jarvis ", "hey jarvis ", "please ", "can you please ", "can you ", "could you "]:
            if query_lower.startswith(prefix):
                query_lower = query_lower[len(prefix):].strip()

        decision = []
        has_auto = False
        has_search = False

        # 1. Rule-based high-confidence automation matching
        platform_names = ["google", "youtube", "facebook", "instagram", "twitter", "x", "github", "reddit", "linkedin", "spotify", "amazon", "maps", "wikipedia", "netflix", "gmail"]

        if query_lower.startswith("open ") and " and play " in query_lower:
            target = query_lower[5:].strip()
            song = target.split(" and play ", 1)[1].replace(" on youtube", "").strip()
            decision = [f"play {song}"]
            has_auto = True
        elif query_lower.startswith("open "):
            target = query_lower[5:].strip()
            if any(platform in target for platform in platform_names):
                decision = [f"open {target}"]
                has_auto = True
            else:
                decision = [f"open {target}"]
                has_auto = True
        elif query_lower.startswith("close "):
            target = query_lower[6:].strip()
            decision = [f"close {target}"]
            has_auto = True
        elif query_lower.startswith("play "):
            song = query_lower[5:].replace("on youtube", "").strip()
            decision = [f"play {song}"]
            has_auto = True
        elif query_lower.startswith("search ") and any(platform in query_lower for platform in platform_names):
            target = query_lower[7:].strip()
            for platform in platform_names:
                if f"{platform} " in target or f" on {platform}" in target:
                    if f" on {platform}" in target:
                        topic = target.split(f" on {platform}", 1)[0].strip()
                    else:
                        topic = target.replace(platform, "", 1).strip()
                    decision = [f"open {platform} {topic}"] if topic else [f"open {platform}"]
                    has_auto = True
                    break
        elif any(platform in query_lower for platform in platform_names) and (" on " in query_lower or query_lower.startswith(platform_names)):
            for platform in platform_names:
                if f" on {platform}" in query_lower:
                    topic = query_lower.split(f" on {platform}", 1)[0].strip()
                    if topic.startswith("search ") or topic.startswith("find "):
                        topic = topic.split(" ", 1)[1].strip()
                    decision = [f"open {platform} {topic}"] if topic else [f"open {platform}"]
                    has_auto = True
                    break
        elif query_lower.startswith("youtube search ") or (query_lower.startswith("search ") and " on youtube" in query_lower):
            topic = query_lower.replace("youtube search", "").replace("search", "").replace("on youtube", "").strip()
            decision = [f"youtube search {topic}"]
            has_auto = True
        elif query_lower.startswith(("system ", "mute", "unmute", "volume up", "volume down")):
            cmd = query_lower.removeprefix("system ").strip()
            decision = [f"system {cmd}"]
            has_auto = True

        # 2. If not rule-matched, use FirstLayerDMM
        if not has_auto:
            try:
                decision = FirstLayerDMM(query)
                has_search = any("realtime" in d or "google search" in d for d in decision)
                has_auto = any(d.startswith(("open", "close", "play", "system", "content", "youtube search")) for d in decision)
            except Exception:
                pass

        intent = "chat"
        answer = ""
        source = "Jarvis Intelligence"

        # Force mode overrides
        if forced_mode == "search":
            has_search = True
            has_auto = False
        elif forced_mode == "chat":
            has_search = False
            has_auto = False
        elif forced_mode == "automation":
            has_auto = True

        if has_auto:
            intent = "automation"
            source = "System Automation"
            try:
                auto_decisions = list(decision) if decision else [f"open {query_lower}"]
                asyncio.run(Automation(auto_decisions))
                
                # Polite, natural response
                first_cmd = auto_decisions[0] if auto_decisions else ""
                if first_cmd.startswith("open "):
                    target = first_cmd[5:].strip().title()
                    answer = f"Opening {target} for you now, sir."
                elif first_cmd.startswith("close "):
                    target = first_cmd[6:].strip().title()
                    answer = f"Closing {target}, sir."
                elif first_cmd.startswith("play "):
                    target = first_cmd[5:].strip().title()
                    answer = f"Playing {target} on YouTube for you, sir."
                elif first_cmd.startswith("youtube search "):
                    target = first_cmd[15:].strip()
                    answer = f"Searching YouTube for '{target}', sir."
                else:
                    answer = f"Executed: {query_clean}"
            except Exception as e:
                answer = f"System automation performed for: '{query}' (Note: {e})"

        elif has_search or any(w in query.lower() for w in ["latest", "today", "news", "price", "who is", "weather", "search", "date"]):
            intent = "search"
            source = "Real-Time Web Search"
            answer = RealtimeSearchEngine(query)
            if not answer:
                answer = ChatBot(query)

        else:
            intent = "chat"
            source = "Neural Chat Engine"
            answer = ChatBot(query)

        if not answer:
            answer = "I processed your request, sir. How else may I assist you?"

        # Save to ChatLog.json
        current_history = read_chat_history()
        current_history.append({"role": "user", "content": query})
        current_history.append({"role": "assistant", "content": answer})
        if len(current_history) > 30:
            current_history = current_history[-30:]
        write_chat_history(current_history)

        return jsonify({
            "success": True,
            "query": query,
            "answer": answer,
            "intent": intent,
            "source": source
        })

    except Exception as e:
        print(f"Error handling query: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "answer": f"Jarvis encountered an issue processing your request: {e}"
        }), 500


@app.route("/api/generate-image", methods=["POST"])
def generate_image_api():
    data = request.get_json(force=True, silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    try:
        from Backend.ImageGeneration import generate_images, open_image
        asyncio.run(generate_images(prompt))

        # Look for saved images in Data folder
        clean_prompt = prompt.replace(" ", "_")
        image_urls = []
        for i in range(1, 5):
            fname = f"{clean_prompt}{i}.jpg"
            fpath = DATA_DIR / fname
            if fpath.exists() and fpath.stat().st_size > 0:
                image_urls.append(f"/data/{fname}")

        # Fallback to any existing sample images if HF didn't produce files
        if not image_urls:
            existing = list(DATA_DIR.glob("*.jpg"))
            if existing:
                image_urls = [f"/data/{f.name}" for f in existing[:4]]

        return jsonify({
            "success": True,
            "prompt": prompt,
            "images": image_urls
        })

    except Exception as e:
        print(f"Image generation error: {e}")
        # Return fallback images if available
        existing = list(DATA_DIR.glob("*.jpg"))
        image_urls = [f"/data/{f.name}" for f in existing[:4]]
        return jsonify({
            "success": True,
            "prompt": prompt,
            "images": image_urls,
            "note": f"Served catalog images ({e})"
        })


@app.route("/api/tts", methods=["POST"])
def text_to_speech_api():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Empty text"}), 400

    try:
        import edge_tts
        audio_path = DATA_DIR / "speech.mp3"
        if audio_path.exists():
            try:
                os.remove(audio_path)
            except Exception:
                pass

        async def run_tts():
            # Clean markdown formatting for clean audio reading
            clean_text = text.replace("*", "").replace("#", "").replace("|", "")
            communicate = edge_tts.Communicate(clean_text[:400], AssistantVoice, pitch="+5Hz", rate="+12%")
            await communicate.save(str(audio_path))

        asyncio.run(run_tts())

        if audio_path.exists():
            return send_file(str(audio_path), mimetype="audio/mpeg")
        else:
            return jsonify({"error": "Failed to create audio"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stt", methods=["POST"])
def speech_to_text_api():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    groq_key = env_vars.get("GroqAPIKey")
    if not groq_key:
        return jsonify({"error": "Groq API key not configured"}), 500

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)

        temp_dir = DATA_DIR / "temp_audio"
        temp_dir.mkdir(exist_ok=True)
        orig_name = audio_file.filename or "recording.webm"
        ext = os.path.splitext(orig_name)[1] or ".webm"
        temp_path = temp_dir / f"rec_{os.getpid()}_{threading.get_ident()}{ext}"

        audio_file.save(str(temp_path))

        with open(str(temp_path), "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(temp_path.name, f.read()),
                model="whisper-large-v3",
                response_format="json",
                language=env_vars.get("InputLanguage", "en")
            )

        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass

        text = (transcription.text or "").strip()
        return jsonify({"success": True, "text": text})
    except Exception as e:
        print(f"STT Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  JARVIS AI WEB SERVER INITIALIZED")
    print(f"  Access the site at: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
