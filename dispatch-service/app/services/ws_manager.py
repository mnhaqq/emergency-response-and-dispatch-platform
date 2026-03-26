from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    """
    Manages active WebSocket connections.
    Clients subscribe to a vehicle_id channel and receive live location updates.
    """

    def __init__(self):
        # vehicle_id -> list of connected websocket clients
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, vehicle_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(vehicle_id, []).append(websocket)

    def disconnect(self, vehicle_id: str, websocket: WebSocket):
        if vehicle_id in self.active:
            self.active[vehicle_id].discard(websocket)

    async def broadcast(self, vehicle_id: str, data: dict):
        """Push location update to all subscribers of this vehicle."""
        dead = []
        for ws in self.active.get(vehicle_id, []):
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active[vehicle_id].remove(ws)


manager = ConnectionManager()
