from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QFont, QPainter, QMovie, QColor, QTextCharFormat, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
from datetime import datetime
import json
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
Assistantname = env_vars.get("Assistantname", "Assistant")
old_chat_message = ""
TempDirPath = os.path.join(PROJECT_ROOT, "Frontend", "Files")
GraphicsDirpath = os.path.join(PROJECT_ROOT, "Frontend", "Graphics")
CHAT_LOG_PATH = os.path.join(PROJECT_ROOT, "Data", "ChatLog.json")
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirpath, exist_ok=True)
os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)


def ensure_chat_history_file():
    if not os.path.exists(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)


def load_chat_history():
    ensure_chat_history_file()
    try:
        with open(CHAT_LOG_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_chat_history(messages):
    ensure_chat_history_file()
    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)


def format_history_message(message):
    role = str(message.get("role", "assistant")).strip().lower()
    content = str(message.get("content", "")).strip()
    if not content:
        return ""
    role_label = "You" if role == "user" else "Assistant"
    timestamp = message.get("timestamp") or datetime.now().strftime("%H:%M")
    return f"[{timestamp}] {role_label}: {content}"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modifier_answer = '\n'.join(non_empty_lines)
    return modifier_answer


def ApplyAppTheme(app):
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, QColor(8, 12, 18))
    palette.setColor(palette.WindowText, QColor(230, 236, 245))
    palette.setColor(palette.Base, QColor(12, 18, 28))
    palette.setColor(palette.AlternateBase, QColor(18, 26, 38))
    palette.setColor(palette.ToolTipBase, QColor(18, 26, 38))
    palette.setColor(palette.ToolTipText, QColor(230, 236, 245))
    palette.setColor(palette.Text, QColor(230, 236, 245))
    palette.setColor(palette.Button, QColor(28, 36, 50))
    palette.setColor(palette.ButtonText, QColor(230, 236, 245))
    palette.setColor(palette.Highlight, QColor(68, 156, 255))
    palette.setColor(palette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "how", "when", "where", "who", "why", "which", "whose", "whom", "is", "are", "was", "were", "do", "does", "did", "can", "could", "should", "would", "may", "might", "must", "shall", "will", "have", "has", "had", "am", "is", "are", "was", "were", "do", "does", "did", "can", "could", "should", "would", "may", "might", "must", "shall", "will", "have", "has", "had", "am", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query = new_query + "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query = new_query + "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Mic.data'), "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    mic_path = os.path.join(TempDirPath, 'Mic.data')
    if not os.path.exists(mic_path):
        return "False"
    with open(mic_path, "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    status_path = os.path.join(TempDirPath, 'Status.data')
    if not os.path.exists(status_path):
        return "Available..."
    with open(status_path, "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirpath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.chat_text_edit = QTextEdit(self)
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            background: rgba(9, 17, 28, 0.95);
            color: #edf6ff;
            border: 1px solid rgba(122, 162, 255, 0.25);
            border-radius: 18px;
            padding: 14px;
            font-size: 13px;
        """)
        self.chat_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_text_edit.setAcceptRichText(False)
        layout.addWidget(self.chat_text_edit)

        self.lable = QLabel("")
        self.lable.setStyleSheet("color: #8be9fd; font-size: 14px; font-weight: 600; background: rgba(12, 20, 32, 0.8); border: 1px solid rgba(109, 182, 255, 0.2); border-radius: 10px; padding: 9px 12px;")
        self.lable.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lable, alignment=Qt.AlignRight)

        self.setStyleSheet("""
            QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: rgba(10, 18, 30, 0.9);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #64c8ff;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        font = QFont()
        font.setPointSize(12)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

    def loadMessages(self):
        global old_chat_message
        try:
            messages = load_chat_history()
            rendered = "\n\n".join(
                [item for item in (format_history_message(msg) for msg in messages) if item]
            )
            if rendered and rendered != old_chat_message:
                self.chat_text_edit.clear()
                self.chat_text_edit.setPlainText(rendered)
                old_chat_message = rendered
                scrollbar = self.chat_text_edit.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"Error loading messages: {e}")

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.lable.setText(messages)
        except Exception:
            self.lable.setText("Available...")

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setLeftMargin(12)
        formatm.setRightMargin(12)
        formatm.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, stacked_widget=None, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(18)

        header = QHBoxLayout()
        self.banner = QLabel(f"{Assistantname.capitalize()} AI")
        self.banner.setAlignment(Qt.AlignLeft)
        self.banner.setStyleSheet("color: #eff7ff; font-size: 32px; font-weight: 700; letter-spacing: 0.8px;")
        header.addWidget(self.banner)
        header.addStretch(1)

        self.status_chip = QLabel("System online")
        self.status_chip.setStyleSheet("color: #9fe7ff; background: rgba(39, 111, 178, 0.2); border: 1px solid rgba(88, 182, 255, 0.35); border-radius: 999px; padding: 8px 14px; font-weight: 600;")
        header.addWidget(self.status_chip)
        main_layout.addLayout(header)

        hero = QFrame()
        hero.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0c1726, stop:1 #0b2336); border: 1px solid rgba(126, 175, 255, 0.3); border-radius: 26px;")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 20, 20, 18)
        hero_layout.setSpacing(22)

        info_container = QVBoxLayout()
        title_label = QLabel("Your personal AI workspace")
        title_label.setStyleSheet("color: #edf7ff; font-size: 28px; font-weight: 700;")
        info_container.addWidget(title_label)

        subtitle = QLabel("Smart search, automation, voice interactions, and contextual chat — all in one streamlined desktop assistant.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #b7cfe9; font-size: 14px; line-height: 1.5;")
        info_container.addWidget(subtitle)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        launch_chat = QPushButton("Open chat")
        launch_chat.setStyleSheet("QPushButton { background: #2ea2ff; color: white; border: none; border-radius: 12px; padding: 12px 18px; font-weight: 700; } QPushButton:hover { background: #4eaefc; }")
        launch_chat.clicked.connect(self.openChatScreen)
        action_row.addWidget(launch_chat)

        clear_chat = QPushButton("New conversation")
        clear_chat.setStyleSheet("QPushButton { background: rgba(255,255,255,0.06); color: #edf7ff; border: 1px solid rgba(160,207,255,0.28); border-radius: 12px; padding: 12px 18px; font-weight: 600; } QPushButton:hover { background: rgba(255,255,255,0.12); }")
        clear_chat.clicked.connect(self.clearConversation)
        action_row.addWidget(clear_chat)
        info_container.addLayout(action_row)
        hero_layout.addLayout(info_container)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: 2px solid rgba(122, 181, 255, 0.5); border-radius: 75px; background: qradialgradient(cx:0.5, cy:0.5, radius: 0.7, fx:0.5, fy:0.5, stop:0 #45c2ff, stop:1 #0d1b2a);")
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        hero_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(hero, stretch=1)

        quick_cards = QHBoxLayout()
        quick_cards.setSpacing(16)
        for title, value in [("Status", "Listening ready"), ("History", "Saved locally"), ("Mode", "AI + Search")]:
            card = QFrame()
            card.setStyleSheet("background: rgba(11, 22, 35, 0.92); border: 1px solid rgba(148, 190, 255, 0.2); border-radius: 18px;")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #8ab5db; font-size: 12px; letter-spacing: 0.7px; text-transform: uppercase;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #edf7ff; font-size: 18px; font-weight: 700;")
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            quick_cards.addWidget(card)
        main_layout.addLayout(quick_cards)

        self.label = QLabel("")
        self.label.setStyleSheet("color: #8be9fd; font-size: 16px; font-weight: 600;")
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #030b13, stop:1 #0a1420);")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

    def openChatScreen(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentIndex(1)

    def clearConversation(self):
        save_chat_history([])

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
                self.status_chip.setText("System online" if not messages else messages)
        except Exception:
            self.label.setText("Available...")
            self.status_chip.setText("System online")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 80, 80)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 80, 80)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        label = QLabel("Conversation")
        label.setStyleSheet("color: #eaf4ff; font-size: 24px; font-weight: 700; padding-left: 6px;")
        header.addWidget(label)
        header.addStretch(1)

        clear_button = QPushButton("Clear chat")
        clear_button.setStyleSheet("QPushButton { background: rgba(255,255,255,0.06); color: #edf7ff; border: 1px solid rgba(160,207,255,0.28); border-radius: 10px; padding: 9px 14px; font-weight: 600; } QPushButton:hover { background: rgba(255,255,255,0.12); }")
        clear_button.clicked.connect(self.clearHistory)
        header.addWidget(clear_button)
        layout.addLayout(header)

        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #02070d, stop:1 #0a1420);")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

    def clearHistory(self):
        save_chat_history([])

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(62)
        self.setStyleSheet("background: #0a111c; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: #eaf2ff; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;")

        layout.addWidget(title_label)
        layout.addStretch(1)

        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setStyleSheet("QPushButton { background:#152231; color:#eaf2ff; border:1px solid #22354e; border-radius:10px; padding:10px 16px; font-weight:600; } QPushButton:hover { background:#1b2d40; }")
        home_button.clicked.connect(self.showHomeScreen)

        message_button = QPushButton("Chat")
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        message_button.setStyleSheet("QPushButton { background:#152231; color:#eaf2ff; border:1px solid #22354e; border-radius:10px; padding:10px 16px; font-weight:600; } QPushButton:hover { background:#1b2d40; }")
        message_button.clicked.connect(self.showChatScreen)

        minimize_button = QPushButton("")
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize2.png')))
        minimize_button.setStyleSheet("QPushButton { background:#152231; border:1px solid #22354e; border-radius:10px; padding:10px; } QPushButton:hover { background:#1b2d40; }")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton("")
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("QPushButton { background:#152231; border:1px solid #22354e; border-radius:10px; padding:10px; } QPushButton:hover { background:#1b2d40; }")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton("")
        close_button.setIcon(QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.setStyleSheet("QPushButton { background:#152231; border:1px solid #22354e; border-radius:10px; padding:10px; } QPushButton:hover { background:#d64545; }")
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def showHomeScreen(self):
        self.stacked_widget.setCurrentIndex(0)  # Switch to InitialScreen (Home)

    def showChatScreen(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to MessageScreen (Chat)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.initUI()

    def initUI(self):
        dekstop = QApplication.desktop()
        screen_width = dekstop.screenGeometry().width()
        screen_height = dekstop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen(stacked_widget=stacked_widget)  # Home screen
        message_screen = MessageScreen()  # Chat screen
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    ApplyAppTheme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface() 