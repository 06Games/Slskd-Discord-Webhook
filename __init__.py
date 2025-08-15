"""
Slskd Discord Webhook - A relay service for Slskd notifications to Discord.
"""

__version__ = "1.0.0"
__author__ = "06Games"

from discord_client import send_to_discord_webhook
from formatters import format_slskd_to_discord
from server import WebhookHandler
from utils import format_bytes, format_speed

__all__ = [
    "send_to_discord_webhook",
    "format_slskd_to_discord", 
    "WebhookHandler",
    "format_bytes",
    "format_speed"
]
