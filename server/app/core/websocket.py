from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        # project_id -> list of (websocket, user_id, user_name)
        self.active_connections: Dict[int, List[tuple]] = {}

    async def connect(self, websocket: WebSocket, project_id: int, user_id: int, user_name: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append((websocket, user_id, user_name))

    def disconnect(self, websocket: WebSocket, project_id: int):
        if project_id in self.active_connections:
            self.active_connections[project_id] = [
                conn for conn in self.active_connections[project_id] if conn[0] != websocket
            ]

    async def broadcast_to_project(self, project_id: int, message: dict, exclude_ws: WebSocket = None):
        if project_id not in self.active_connections:
            return
        dead = []
        for ws, uid, uname in self.active_connections[project_id]:
            if ws == exclude_ws:
                continue
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, project_id)

    def get_online_users(self, project_id: int) -> List[dict]:
        if project_id not in self.active_connections:
            return []
        return [{"user_id": uid, "user_name": uname} for _, uid, uname in self.active_connections[project_id]]


manager = ConnectionManager()
