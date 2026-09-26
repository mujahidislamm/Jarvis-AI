from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAT_LOG_PATH = PROJECT_ROOT / "Data" / "ChatLog.json"


def _load_chat_history() -> list:
    """Read chat messages from the JSON log file."""
    try:
        if CHAT_LOG_PATH.exists():
            with open(CHAT_LOG_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def _save_chat_history(messages: list) -> None:
    """Overwrite the JSON log file."""
    CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(messages, fh, ensure_ascii=False, indent=4)


class _HistoryItemWidget(QFrame):
    """A single chat-history entry showing role icon, preview text, and timestamp."""

    def __init__(self, message: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("history-item")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Role icon
        role = str(message.get("role", "assistant")).strip().lower()
        icon_text = "🧑" if role == "user" else "🤖"
        icon = QLabel(icon_text)
        icon.setObjectName("history-role-icon")
        icon.setAlignment(Qt.AlignTop)
        layout.addWidget(icon)

        # Text column
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(3)

        content = str(message.get("content", "")).strip()
        preview = (content[:80] + "…") if len(content) > 80 else content
        msg_label = QLabel(preview)
        msg_label.setObjectName("history-message-text")
        msg_label.setWordWrap(True)
        text_col.addWidget(msg_label)

        timestamp = message.get("timestamp") or ""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M")
        role_label = "You" if role == "user" else "Jarvis"
        ts_label = QLabel(f"{role_label}  ·  {timestamp}")
        ts_label.setObjectName("history-timestamp")
        text_col.addWidget(ts_label)

        layout.addLayout(text_col, 1)


class ChatHistorySidebar(QWidget):
    """Collapsible sidebar that displays chat history from ChatLog.json."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat-sidebar")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(300)

        self._prev_hash: str = ""

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        # ── Header row ──
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        header_label = QLabel("💬  Chat History")
        header_label.setObjectName("sidebar-header")
        header_row.addWidget(header_label)
        header_row.addStretch(1)

        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("sidebar-clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_history)
        header_row.addWidget(clear_btn)
        root_layout.addLayout(header_row)

        # ── New Chat button ──
        new_chat_btn = QPushButton("＋  New Conversation")
        new_chat_btn.setObjectName("sidebar-new-chat")
        new_chat_btn.setCursor(Qt.PointingHandCursor)
        new_chat_btn.clicked.connect(self._clear_history)
        root_layout.addWidget(new_chat_btn)

        # ── Scroll area for history items ──
        self._scroll = QScrollArea()
        self._scroll.setObjectName("sidebar-scroll-area")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("sidebar-scroll-content")
        self._items_layout = QVBoxLayout(self._scroll_content)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(8)
        self._items_layout.addStretch(1)

        self._scroll.setWidget(self._scroll_content)
        root_layout.addWidget(self._scroll, 1)

        # ── Empty-state label ──
        self._empty_label = QLabel("No messages yet.\nStart a conversation!")
        self._empty_label.setObjectName("sidebar-empty-label")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.setVisible(True)
        self._items_layout.insertWidget(0, self._empty_label)

        # ── Auto-refresh timer ──
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)
        self._refresh()

    # ── Public API ──

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())

    # ── Private helpers ──

    def _refresh(self):
        """Reload messages from disk if the file has changed."""
        messages = _load_chat_history()
        content_hash = str(len(messages)) + ("" if not messages else str(messages[-1]))
        if content_hash == self._prev_hash:
            return
        self._prev_hash = content_hash
        self._rebuild_items(messages)

    def _rebuild_items(self, messages: list):
        """Clear and rebuild all item widgets."""
        # Remove existing item widgets (keep the stretch at the end)
        while self._items_layout.count() > 1:
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_messages = bool(messages)

        if has_messages:
            # Show most-recent first (reversed)
            for msg in reversed(messages):
                widget = _HistoryItemWidget(msg, self._scroll_content)
                # Insert before the stretch
                self._items_layout.insertWidget(self._items_layout.count() - 1, widget)

        # Empty-state label
        if not has_messages:
            self._empty_label = QLabel("No messages yet.\nStart a conversation!")
            self._empty_label.setObjectName("sidebar-empty-label")
            self._empty_label.setAlignment(Qt.AlignCenter)
            self._empty_label.setWordWrap(True)
            self._items_layout.insertWidget(0, self._empty_label)

    def _clear_history(self):
        _save_chat_history([])
        self._prev_hash = ""
        self._refresh()
