import importlib.util
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Prefer the working desktop UI entry point, while keeping the legacy entry point as a fallback.
try:
    frontend_main_path = PROJECT_ROOT / "Frontend" / "main.py"
    if not frontend_main_path.exists():
        frontend_main_path = PROJECT_ROOT / "frontend" / "main.py"
    if frontend_main_path.exists():
        spec = importlib.util.spec_from_file_location("jarvis_frontend_main", str(frontend_main_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if __name__ == "__main__":
            raise SystemExit(module.main())
except Exception:
    from Frontend.GUI import (
        GraphicalUserInterface,
        SetAssistantStatus,
        ShowTextToScreen,
        TempDirectoryPath,
        SetMicrophoneStatus,
        AnswerModifier,
        QueryModifier,
        GetAssistantStatus,
        GetMicrophoneStatus
    )
    from Backend.Model import FirstLayerDMM
    from Backend.RealtimeSearchEngine import RealtimeSearchEngine
    from Backend.Automation import Automation
    from Backend.SpeechToText import SpeechRecognition
    from Backend.Chatbot import ChatBot
    from Backend.TextToSpeech import TextToSpeech
    from dotenv import dotenv_values
    from asyncio import run
    from time import sleep
    import subprocess
    import threading
    import json

    DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
    FILES_DIR = os.path.join(PROJECT_ROOT, "Frontend", "Files")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)

    env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
    Username = env_vars.get("Username", "User")
    Assistantname = env_vars.get("Assistantname", "Assistant")

    DefaultMessage = f"""{Username}  : Hello {Assistantname}! How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

    Function = ["open", "close", "play", "system", "content", "google search", "youtube search"]
    subprocess_list = []

    def ShowDefaultChatIfNoChats():
        try:
            chat_log_path = os.path.join(DATA_DIR, "ChatLog.json")
            temp_path = TempDirectoryPath("Responses.data")
            os.makedirs(DATA_DIR, exist_ok=True)

            if not os.path.exists(chat_log_path) or os.path.getsize(chat_log_path) < 5:
                with open(chat_log_path, "w", encoding='utf-8') as file:
                    json.dump([
                        {"role": "assistant", "content": "Welcome! I am ready to help you with search, automation, and daily tasks."}
                    ], file, ensure_ascii=False, indent=4)

            with open(temp_path, "w", encoding='utf-8') as temp_file:
                temp_file.write("Welcome! I am ready to help you with search, automation, and daily tasks.")
        except Exception as e:
            print(f"Error processing ChatLog.json: {e}")

    def ReadChatlogJson():
        try:
            with open(os.path.join(DATA_DIR, "ChatLog.json"), "r", encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading ChatLog.json: {e}")
            return []

    def chatLogIntegration():
        try:
            json_data = ReadChatlogJson()
            formatted_chatlog = "\n".join(
                f"{Username if entry['role'] == 'user' else Assistantname}: {entry['content']}"
                for entry in json_data
            )

            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write(AnswerModifier(formatted_chatlog))
        except Exception as e:
            print(f"Error integrating chat log: {e}")

    def ShowChatsOnGUI():
        try:
            db_path = TempDirectoryPath('Database.data')
            with open(db_path, "r", encoding='utf-8') as file:
                data = file.read().strip()
                if data:
                    with open(db_path, "w", encoding='utf-8') as file:
                        file.write(data)
        except Exception as e:
            print(f"Error displaying chat on GUI: {e}")

    def InitialExecution():
        SetMicrophoneStatus("False")
        ShowTextToScreen("")
        ShowDefaultChatIfNoChats()
        chatLogIntegration()
        ShowChatsOnGUI()

    InitialExecution()

    def MainExecution():
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)

        G = any(i.startswith("general") for i in Decision)
        R = any(i.startswith("realtime") for i in Decision)

        Merged_query = " and ".join(
            " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
        )

        for queries in Decision:
            if "generate " in queries:
                ImageGenerationQuery = queries
                ImageExecution = True

        for queries in Decision:
            if not TaskExecution and any(queries.startswith(func) for func in Function):
                run(Automation(list(Decision)))
                TaskExecution = True

        if ImageExecution:
            try:
                image_generation_path = os.path.join(FILES_DIR, "ImageGeneration.data")
                with open(image_generation_path, "w", encoding='utf-8') as file:
                    file.write(f"{ImageGenerationQuery},True")
                p1 = subprocess.Popen(['python', os.path.join(PROJECT_ROOT, 'Backend', 'ImageGeneration.py')],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                subprocess_list.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        else:
            Answer = ChatBot(QueryModifier(Query))

        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)

        if "exit" in Decision:
            os._exit(0)

    def FirstThread():
        while True:
            if GetMicrophoneStatus() == "True":
                MainExecution()
            else:
                if GetAssistantStatus() != "Available...":
                    SetAssistantStatus("Available...")
            sleep(0.1)

    def SecondThread():
        GraphicalUserInterface()

    if __name__ == "__main__":
        thread1 = threading.Thread(target=FirstThread, daemon=True)
        thread1.start()
        SecondThread()