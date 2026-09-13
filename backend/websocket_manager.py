from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio
from datetime import datetime


class WebSocketManager:
    def __init__(self):
        # Store active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        metadata = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        self.connection_metadata[websocket] = metadata
        
        # Send connection confirmation
        await self.send_personal_message(websocket, {
            "type": "connected",
            "data": {"client_id": metadata["client_id"]},
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message to websocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Send a message to all active WebSocket connections"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def send_status_update(self, websocket: WebSocket, status: str, details: dict = None):
        """Send a status update to a specific connection"""
        message = {
            "type": "status",
            "data": {
                "status": status,
                "details": details or {}
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(websocket, message)

    async def send_agent_update(self, websocket: WebSocket, agent_name: str, status: str, data: dict = None):
        """Send an agent-specific status update"""
        message = {
            "type": "agent_update",
            "data": {
                "agent": agent_name,
                "status": status,
                "data": data or {}
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(websocket, message)

    async def send_stream_chunk(self, websocket: WebSocket, chunk: str, is_final: bool = False):
        """Send a streaming text chunk (for LLM responses)"""
        message = {
            "type": "stream_chunk",
            "data": {
                "chunk": chunk,
                "is_final": is_final
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(websocket, message)

    async def send_error(self, websocket: WebSocket, error: str, details: dict = None):
        """Send an error message"""
        message = {
            "type": "error",
            "data": {
                "error": error,
                "details": details or {}
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(websocket, message)

    async def send_complete(self, websocket: WebSocket, result: dict):
        """Send a completion message with final results"""
        message = {
            "type": "complete",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(websocket, message)

    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

    def get_connection_info(self, websocket: WebSocket) -> dict:
        """Get metadata for a specific connection"""
        return self.connection_metadata.get(websocket, {})


# Global WebSocket manager instance
manager = WebSocketManager()