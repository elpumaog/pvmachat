from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import database

app = FastAPI()

# Lista para almacenar conexiones activas
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    try:
        while True:
            message = await websocket.receive_text()
            formatted_message = f"{username}: {message}"
            database.save_message(username, message)
            for user, connection in active_connections.items():
                await connection.send_text(formatted_message)
    except WebSocketDisconnect:
        del active_connections[username]
        for user, connection in active_connections.items():
            await connection.send_text(f"{username} se ha desconectado")