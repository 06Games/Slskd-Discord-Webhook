"""
Discord webhook formatters for Slskd notifications.
"""

import os
import json
from typing import Dict, Any, Optional

from utils import format_bytes, format_speed


def _create_base_webhook_payload() -> Dict[str, Any]:
    """Create base Discord webhook payload structure."""
    return {
        "username": "Slskd",
        "avatar_url": None  # f"{os.getenv('SLSKD_URL')}/favicon.ico" if os.getenv('SLSKD_URL') else None
    }


def _create_message_embed(username: str, message: str, timestamp: str, color: int, footer_text: str) -> Dict[str, Any]:
    """Create embed for chat messages."""
    slskd_url = os.getenv('SLSKD_URL')
    return {
        "color": color,
        "author": {
            "name": username,
            "url": f"{slskd_url}/chat" if slskd_url else None
        },
        "description": message,
        "footer": {"text": footer_text},
        "timestamp": timestamp
    }


def _format_room_message(data: Dict[Any, Any]) -> Optional[Dict[str, Any]]:
    """Format room message notification."""
    msg_data = data.get("message", {})
    
    if msg_data.get("wasReplayed", False):
        return None  # Ignore replayed messages
    
    username = msg_data.get("username", "Unknown User")
    room_name = msg_data.get("roomName", "Unknown Room")
    timestamp = msg_data.get("timestamp", "")
    message = msg_data.get("message", "")
    
    payload = _create_base_webhook_payload()
    payload.update({
        "content": "💬 You've received a room message",
        "embeds": [_create_message_embed(username, message, timestamp, 5793266, f"in {room_name}")]
    })
    return payload


def _format_private_message(data: Dict[Any, Any]) -> Optional[Dict[str, Any]]:
    """Format private message notification."""
    msg_data = data.get("message", {})
    
    if msg_data.get("wasReplayed", False):
        return None  # Ignore replayed messages
    
    username = msg_data.get("username", "Unknown User")
    timestamp = msg_data.get("timestamp", "")
    message = msg_data.get("message", "")
    
    payload = _create_base_webhook_payload()
    payload.update({
        "content": "📩 You've received a private message",
        "embeds": [_create_message_embed(username, message, timestamp, 3447003, "Private Message")]
    })
    return payload


def _format_upload_complete(data: Dict[Any, Any]) -> Dict[str, Any]:
    """Format upload complete notification."""
    transfer = data.get("transfer", {})
    username = transfer.get("username", "Unknown User")
    local_filename = data.get("localFilename", "Unknown File")
    timestamp = data.get("timestamp", "")
    
    # Extract filename and create description
    filename = os.path.basename(local_filename)
    file_size = transfer.get("size", 0)
    average_speed = transfer.get("averageSpeed", 0)
    elapsed_time = transfer.get("elapsedTime", "Unknown")
    state = transfer.get("state", "Unknown")
    
    description = (
        f"**{filename}**\n"
        f"📁 Size: {format_bytes(file_size)}\n"
        f"⚡ Speed: {format_speed(average_speed)}\n"
        f"⏱️ Duration: {elapsed_time}\n"
        f"✅ Status: {state}"
    )
    
    payload = _create_base_webhook_payload()
    payload.update({
        "content": "⬆️ Upload completed successfully!",
        "embeds": [{
            "color": 3066993,
            "author": {"name": username},
            "description": description,
            "footer": {"text": f"Upload to: {username}"},
            "timestamp": timestamp
        }]
    })
    return payload


def _format_unknown_message(data: Dict[Any, Any], message_type: str) -> Dict[str, Any]:
    """Format unknown message type notification."""
    timestamp = data.get("timestamp", "")
    
    payload = _create_base_webhook_payload()
    payload.update({
        "content": f"📢 Slskd Notification: {message_type}",
        "embeds": [{
            "color": 9807270,
            "title": message_type,
            "description": f"```json\n{json.dumps(data, indent=2)}\n```",
            "footer": {"text": "Raw notification data"},
            "timestamp": timestamp
        }]
    })
    return payload


def format_slskd_to_discord(data: Dict[Any, Any]) -> Optional[Dict[str, Any]]:
    """
    Format Slskd notification data into Discord webhook format.
    
    Args:
        data: Raw Slskd notification data
        
    Returns:
        Formatted Discord webhook payload or None if message should be ignored
    """
    message_type = data.get("type", "Unknown")
    
    # Message type handlers
    handlers = {
        "RoomMessageReceived": _format_room_message,
        "PrivateMessageReceived": _format_private_message,
        "UploadFileComplete": _format_upload_complete,
    }
    
    handler = handlers.get(message_type)
    if handler:
        return handler(data)
    else:
        return _format_unknown_message(data, message_type)
