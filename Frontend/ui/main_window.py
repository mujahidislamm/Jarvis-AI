from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from Frontend.bridge.assistant_bridge import AssistantBridge
from Frontend.ui.hero import HeroWidget
from Frontend.ui.history_rail import ChatHistorySidebar
from Frontend.ui.input_bar import InputBar
from Frontend.ui.quick_actions import QuickActionsRow
from Frontend.ui.response_panel import ResponsePanel
from Frontend.ui.titlebar import TitleBar

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STYLES_PATH = PROJECT_ROOT / "Frontend" / "styles" / "theme.qss"
# Fallback for case-insensitive filesystems
if not STYLES_PATH.exists():
    STYLES_PATH = PROJECT_ROOT / "frontend" / "styles" / "theme.qss"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 780)
        self.setMinimumSize(900, 640)
        self.setObjectName("main-window")

        self.bridge = AssistantBridge(self)

        # ── Root layout: H-split between main content and sidebar ──
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Main content column ──
        main_col = QWidget()
        main_col.setObjectName("main-column")
        self.main_layout = QVBoxLayout(main_col)
        self.main_layout.setContentsMargins(18, 10, 18, 18)
        self.main_layout.setSpacing(16)

        self.titlebar = TitleBar(self)
        self.hero = HeroWidget(self)
        self.input_bar = InputBar(self)
        self.quick_actions = QuickActionsRow(self)
        self.response_panel = ResponsePanel(self)

        self.main_layout.addWidget(self.titlebar)
        self.main_layout.addWidget(self.hero)
        self.main_layout.addWidget(self.input_bar)
        self.main_layout.addWidget(self.quick_actions)
        self.main_layout.addWidget(self.response_panel)

        root.addWidget(main_col, 1)

        # ── Chat History Sidebar ──
        self.sidebar = ChatHistorySidebar(self)
        self.sidebar.setVisible(True)
        root.addWidget(self.sidebar, 0)

        self._connect_signals()
        self._apply_theme()
        self._sync_state("IDLE")

    def _apply_theme(self):
        try:
            with open(str(STYLES_PATH), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"[Jarvis AI] Theme file not found at {STYLES_PATH}")

    def _connect_signals(self):
        self.bridge.state_changed.connect(self._sync_state)
        self.bridge.transcript_ready.connect(self._set_transcript)
        self.bridge.response_ready.connect(self._set_response)
        self.bridge.error_occurred.connect(self._set_error)

        self.input_bar.mic_button.clicked.connect(self._toggle_listen)
        self.input_bar.send_button.clicked.connect(self._send_text)
        self.quick_actions.cards[0].run_btn.clicked.connect(lambda: self.bridge.trigger_action("Open App"))
        self.quick_actions.cards[1].run_btn.clicked.connect(lambda: self.bridge.trigger_action("Web Search"))
        self.quick_actions.cards[2].run_btn.clicked.connect(lambda: self.bridge.trigger_action("Automation"))

        # Sidebar toggle from title bar
        self.titlebar.sidebar_toggle.clicked.connect(self.sidebar.toggle_visibility)

    def _sync_state(self, state: str):
        self.hero.set_state(state)
        self.input_bar.set_state(state)

    def _set_transcript(self, text: str):
        self.response_panel.set_query(text)
        self.response_panel.setVisible(True)

    def _set_response(self, text: str):
        self.response_panel.set_answer(text)

    def _set_error(self, message: str):
        self.response_panel.set_error(message)

    def _toggle_listen(self):
        self.bridge.set_state("LISTENING")
        self.response_panel.set_query("Listening for voice input...")
        self.response_panel.setVisible(True)

    def _send_text(self):
        text = self.input_bar.input_field.text().strip()
        if text:
            self.input_bar.input_field.clear()
            self._set_transcript(text)
            self.bridge.process_query(text)
