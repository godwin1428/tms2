"""
TMS — WebSocket Signaling
Room-based WebSocket for chat, WebRTC signaling, vitals streaming.
"""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from typing import Dict, Set
from ..auth.jwt_handler import verify_token

router = APIRouter()

# Room → set of connected WebSockets
rooms: Dict[str, Set[WebSocket]] = {}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = Query(None)):
    """WebSocket endpoint for consultation rooms."""
    if not token or not verify_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    # Add to room
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(websocket)

    try:
        # Notify room about new participant
        await broadcast(room_id, {
            "type": "system",
            "message": "A participant has joined the room",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, exclude=websocket)

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                message = {"type": "chat", "message": data}

            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.now(timezone.utc).isoformat()

            msg_type = message.get("type", "chat")

            if msg_type == "chat":
                # Broadcast chat message to all in room
                await broadcast(room_id, message)
            elif msg_type == "signal":
                # WebRTC signaling — forward to other peers
                await broadcast(room_id, message, exclude=websocket)
            elif msg_type == "vitals":
                # Vitals data — broadcast to all (doctor sees patient vitals)
                await broadcast(room_id, message)
            elif msg_type == "prescription_update":
                # Live prescription building — broadcast to patient
                await broadcast(room_id, message)
            else:
                await broadcast(room_id, message)

    except WebSocketDisconnect:
        rooms[room_id].discard(websocket)
        if not rooms[room_id]:
            del rooms[room_id]
        else:
            await broadcast(room_id, {
                "type": "system",
                "message": "A participant has left the room",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })


async def broadcast(room_id: str, message: dict, exclude: WebSocket = None):
    """Broadcast a message to all WebSockets in a room."""
    if room_id not in rooms:
        return
    dead = set()
    for ws in rooms[room_id]:
        if ws == exclude:
            continue
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.add(ws)
    rooms[room_id] -= dead
