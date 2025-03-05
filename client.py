import sys
import asyncio
import websockets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon, QMenu, QWidgetAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import database

class WebSocketThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.websocket = None
        self.loop = None
    
    async def connect_to_server(self):
        try:
            self.websocket = await websockets.connect(f"ws://localhost:8000/ws/{self.client_id}")
            while True:
                message = await self.websocket.recv()
                self.message_received.emit(message)
        except Exception as e:
            self.message_received.emit(f"Error: {e}")
    
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def send_message(self, message):
        if self.websocket:
            await self.websocket.send(message)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesion")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Ingrese su nombre de usuario:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.login_button = QPushButton("Entrar al chat")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text().strip()
        if username:
            if database.add_user(username): # Guardar usuario en la base de datos
                self.chat_window = ChatClient(username)
                self.chat_window.show()
                self.close()
            else:
                self.label.setText("El usuario ya existe, usa otro nombre.")

class ChatClient(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username

        self.setWindowTitle(f"Chat en {username}")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        self.websocket_thread = WebSocketThread(self.username)
        self.websocket_thread.message_received.connect(self.display_message)
        self.websocket_thread.start()

        self.load_previous_messages()
    
    def load_previous_messages(self):
        messages = database.get_messages()
        for username, message in messages:
            self.chat_display.append(f"{username}: {message}")

    def display_message(self, message):
        self.chat_display.append(message)
    
    def send_message(self):
        message = self.message_input.text().strip()
        if message:

            asyncio.run_coroutine_threadsafe(self.websocket_thread.send_message(message),
                                             self.websocket_thread.loop)
            database.save_message(self.username, message)
            self.message_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())