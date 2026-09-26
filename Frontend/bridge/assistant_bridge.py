from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, QTimer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AssistantBridge(QObject):
    """Bridge connecting frontend UI components to real Jarvis AI backend services."""

    state_changed = Signal(str)
    transcript_ready = Signal(str)
    response_ready = Signal(str)
    speaking_started = Signal()
    speaking_stopped = Signal()
    amplitude_update = Signal(float)
    error_occurred = Signal(str)
    action_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "IDLE"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._emit_demo_cycle)
        self._demo_step = 0
        self._is_busy = False

    def start_demo(self):
        """Optional demo cycle mode."""
        self._timer.start(2400)
        self.state_changed.emit("IDLE")

    def stop_demo(self):
        """Stops demo cycling."""
        if self._timer.isActive():
            self._timer.stop()

    def _emit_demo_cycle(self):
        if self._is_busy:
            return
        self._demo_step = (self._demo_step + 1) % 6
        if self._demo_step == 0:
            self.state_changed.emit("IDLE")
            self.response_ready.emit("Ready. Ask Jarvis anything or select a quick action.")
        elif self._demo_step == 1:
            self.state_changed.emit("LISTENING")
            self.transcript_ready.emit("What is the latest tech news?")
            self.amplitude_update.emit(0.55)
        elif self._demo_step == 2:
            self.state_changed.emit("PROCESSING")
            self.amplitude_update.emit(0.8)
        elif self._demo_step == 3:
            self.state_changed.emit("RESPONDING")
            self.response_ready.emit(
                "Jarvis is equipped with real-time web search, intelligent reasoning, image generation, and system automation."
            )
        elif self._demo_step == 4:
            self.state_changed.emit("SPEAKING")
            self.speaking_started.emit()
            self.amplitude_update.emit(0.9)
        elif self._demo_step == 5:
            self.speaking_stopped.emit()
            self.state_changed.emit("IDLE")
            self.amplitude_update.emit(0.2)

    def set_state(self, state: str):
        self._state = state
        self.state_changed.emit(state)

    def trigger_action(self, action_name: str):
        self.action_triggered.emit(action_name)
        if action_name == "Open App":
            self.process_query("open notepad")
        elif action_name == "Web Search":
            self.process_query("latest tech news")
        elif action_name == "Automation":
            self.process_query("what can you automate?")

    def emit_error(self, message: str):
        self.error_occurred.emit(message)
        self.state_changed.emit("ERROR")

    def emit_response(self, text: str):
        self.response_ready.emit(text)

    def emit_transcript(self, text: str):
        self.transcript_ready.emit(text)

    def emit_speaking_start(self):
        self.speaking_started.emit()

    def emit_speaking_stop(self):
        self.speaking_stopped.emit()

    def process_query(self, query: str, speak: bool = False):
        """Asynchronously processes a user query with backend AI modules."""
        if not query.strip() or self._is_busy:
            return

        self.stop_demo()
        self._is_busy = True
        self.set_state("PROCESSING")
        self.emit_transcript(query)

        def worker():
            try:
                from Backend.Chatbot import ChatBot
                from Backend.RealtimeSearchEngine import RealtimeSearchEngine
                from Backend.Model import FirstLayerDMM
                from asyncio import run as async_run
                from Backend.Automation import Automation

                cleaned_query = query.strip()
                decision = []
                try:
                    decision = FirstLayerDMM(cleaned_query)
                except Exception:
                    pass

                has_search = any("realtime" in d or "google search" in d for d in decision)
                has_auto = any(d.startswith(("open", "close", "play", "system", "content")) for d in decision)

                if has_auto:
                    self.set_state("PROCESSING")
                    try:
                        async_run(Automation(list(decision)))
                        answer = f"Executed automated action for: {query}"
                    except Exception as e:
                        answer = f"Automation encountered an issue: {e}"
                elif has_search or any(w in cleaned_query.lower() for w in ["latest", "today", "news", "price", "who is", "weather", "search"]):
                    self.set_state("SEARCHING")
                    answer = RealtimeSearchEngine(cleaned_query)
                else:
                    self.set_state("PROCESSING")
                    answer = ChatBot(cleaned_query)

                if not answer:
                    answer = "I've processed your request."

                self.emit_response(answer)

                if speak:
                    try:
                        self.set_state("SPEAKING")
                        self.emit_speaking_start()
                        from Backend.TextToSpeech import TTS
                        TTS(answer)
                    except Exception:
                        pass
                    finally:
                        self.emit_speaking_stop()

                self.set_state("IDLE")

            except Exception as e:
                self.emit_error(f"Error: {e}")
                self.set_state("ERROR")
            finally:
                self._is_busy = False

        threading.Thread(target=worker, daemon=True).start()
