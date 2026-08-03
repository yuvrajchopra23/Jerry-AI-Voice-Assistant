import sys
import threading
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QVBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QCursor

class Signals(QObject):
    response_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)

signals = Signals()

JERRY_URL = "http://127.0.0.1:5000"

def check_online():
    try:
        r = requests.get(JERRY_URL, timeout=2)
        print("Status:", r.status_code)
        return True
    except Exception as e:
        print("ERROR:", e)
        return False

def send_to_jerry(text: str):
    def _send():
        try:
            resp = requests.post(
                f"{JERRY_URL}/command",
                json={"text": text},
                timeout=30
            )

            print(resp.status_code)
            print(resp.text)

            if resp.ok:
                data = resp.json()
                signals.response_received.emit(
                    data.get("response", "Done.")
                )
            else:
                signals.response_received.emit(
                    f"Server Error ({resp.status_code})"
                )

        except Exception as e:
            signals.response_received.emit(str(e))

    threading.Thread(target=_send, daemon=True).start()

#Main widget
class JerryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.expanded = False
        self.drag_pos = QPoint()
        self.is_online = False
        self._build_ui()
        self._check_connection()

        #check connection every 10 secs
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_connection)
        self.timer.start(10000)

        signals.response_received.connect(self._show_response)
        signals.status_changed.connect(self._update_status)

    def _build_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(48,48)

        #move to bottom right corner
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - 70, screen.height() - 100)

        #bubble button
        self.bubble = QPushButton("j", self)
        self.bubble.setFixedSize(48,48)
        self.bubble.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.bubble.clicked.connect(self._toggle_expand)
        self.bubble.setCursor(QCursor(Qt.PointingHandCursor))
        self._style_button(online=False)

        #expanded Panel
        self.panel = QFrame(self)
        self.panel.setFixedSize(300, 160)
        self.panel.move(0, 52)
        self.panel.hide()
        self.panel.setStyleSheet("""
            QFrame{
            background-color: #111111;
            border: 1px solid #7c6aff;
            border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(12,10,12,10)
        layout.setSpacing(8)

        #status label
        self.status_label = QLabel("Connecting...")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #888888; background: transparent; border: none;")
        layout.addWidget(self.status_label)

        #response label
        self.response_label = QLabel("")
        self.response_label.setFont(QFont("Segoe UI", 9))
        self.response_label.setStyleSheet("color: #cccccc; background: transparent; border: none;")
        self.response_label.setWordWrap(True)
        self.response_label.setFixedHeight(40)
        layout.addWidget(self.response_label)

        #input row
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.setFont(QFont("Segoe UI", 9))
        self.input_field.setFixedHeight(32)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 0 8px;
            }
            QLineEdit:focus {
                border: 1px solid #7c6aff;
            }
        """)
        self.input_field.returnPressed.connect(self._send_text)
        input_row.addWidget(self.input_field)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(32, 32)
        send_btn.setCursor(QCursor(Qt.PointingHandCursor))
        send_btn.setStyleSheet("""
            QPushButton {
                background: #7c6aff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover { background: #6a59e0; }
        """)
        send_btn.clicked.connect(self._send_text)
        input_row.addWidget(send_btn)

        layout.addLayout(input_row)

        # Bottom row — mic + close
        bottom_row = QHBoxLayout()

        self.mic_btn = QPushButton("🎤 Speak")
        self.mic_btn.setFixedHeight(28)
        self.mic_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                color: #888;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                font-size: 11px;
            }
            QPushButton:hover { border-color: #7c6aff; color: #7c6aff; }
        """)
        self.mic_btn.clicked.connect(self._start_voice)
        bottom_row.addWidget(self.mic_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                color: #555;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
            QPushButton:hover { border-color: #ff5555; color: #ff5555; }
        """)
        close_btn.clicked.connect(self._toggle_expand)
        bottom_row.addWidget(close_btn)

        layout.addLayout(bottom_row)

    def _style_button(self, online: bool):
        color = "#7c6aff" if online else "#555555"
        self.bubble.setStyleSheet(f"""
            QPushButton{{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 24px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
            background-color: {"#6a59e0" if online else "#666666"};
            }}
        """)

    def _toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.setFixedSize(300, 220)
            self.panel.show()
            self.input_field.setFocus()
        else:
            self.panel.hide()
            self.setFixedSize(48,48)

    def _check_connection(self):
        def _check():
            online = check_online()
            print("online =", online)

            self.is_online = online

            if online:
                self.status_label.setText("● Online — Ready")
                self.status_label.setStyleSheet(
                    "color:#4caf50; background:transparent; border:none;"
                )
            else:
                self.status_label.setText("● Offline — Start Jerry server")
                self.status_label.setStyleSheet(
                    "color:#ff5555; background:transparent; border:none;"
                )

            self._style_button(online)

        threading.Thread(target=_check, daemon=True).start()

    def _send_text(self):
        text = self.input_field.text().strip()
        if not text:
            return
        if not self.is_online:
            self._show_response("Jerry is offline. Start Jerry first.")
            return
        self.input_field.clear()
        self.response_label.setText("Thinking...")
        self.response_label.setStyleSheet("color: #888888; background: transparent; border: none;")
        send_to_jerry(text)

    def _start_voice(self):
        if not self.is_online:
            self._show_response("Jerry is offline.")
            return
        self.mic_btn.setText("🔴 Listening...")
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;    
                color: #ff5555;
                border: 1px solid #ff5555;
                border-radius: 6px;
                font-size: 11px;
            }
        """)
        self.response_label.setText("Listening...")

        def _listen():
            try:
                from voice.listener import listen
                command = listen()
                if command:
                    signals.status_changed.emit("thinking")
                    send_to_jerry(command)
                else:
                    signals.response_received.emit("Didn't catch that.")
            except Exception as e:
                signals.response_received.emit(f"Mic error: {e}")

            # Reset mic button
            self.mic_btn.setText("🎤 Speak")
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #888;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    font-size: 11px;
                }
                QPushButton:hover { border-color: #7c6aff; color: #7c6aff; }
            """)

        threading.Thread(target=_listen, daemon=True).start()

    def _show_response(self, text: str):
        self.response_label.setText(text[:80] + "..." if len(text) > 80 else text)
        self.response_label.setStyleSheet("color: #cccccc; background: transparent; border: none;")

    def _update_status(self, status: str):
        labels = {
            "thinking": "● Thinking...",
            "ready":    "● Ready",
            "listening":"● Listening..."
        }
        self.status_label.setText(labels.get(status, status))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)

def run_widget():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        widget = JerryWidget()
        widget.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    run_widget()