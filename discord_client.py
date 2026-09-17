"""
Discord webhook client for sending notifications.
"""

import json
import logging
from typing import Any

import requests

from formatters import format_slskd_to_discord

logger = logging.getLogger(__name__)


def send_to_discord_webhook(webhook_url: str, data: dict[Any, Any]) -> bool:
    """
    Send data to a Discord webhook.

    Args:
        webhook_url: Discord webhook URL
        data: Dictionary containing the data to send

    Returns:
        True if successful, False otherwise
    """
    try:
        payload = format_slskd_to_discord(data)
        if payload is None:
            logger.info(f"🚫 Ignored Slskd '{data.get('type')}' notification")
            return True

        logger.info(f"🎨 Formatted Slskd '{data.get('type')}' notification for Discord")
        logger.debug(json.dumps(payload))

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        response.raise_for_status()
        logger.info(
            f"✅ Successfully sent data to Discord webhook (Status: {response.status_code})"
        )
        return True

    except requests.exceptions.RequestException as e:
        error_text = ""
        if hasattr(e, "response") and e.response is not None:
            error_text = e.response.text
        logger.error(f"❌ Error sending to Discord webhook: {e}\n{error_text}")
        return False
    except Exception as e:  # noqa: BLE001
        logger.error(f"❌ Unexpected error sending to Discord: {e}")
        return False
