#!/usr/bin/env python3
"""
Slskd Discord Webhook Relay Server

A lightweight HTTP server that receives webhooks from Slskd and forwards
formatted notifications to Discord via webhook.
"""

import os
import sys
import signal
import logging
from http.server import HTTPServer

from server import WebhookHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)


def main():
    """
    Main function to start the webhook server.
    """
    # Configuration
    HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')  # Listen on all interfaces by default
    PORT = int(os.getenv('WEBHOOK_PORT', '8080'))  # Default port 8080
    
    # Check if Discord webhook URL is configured
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        logger.error("❌ DISCORD_WEBHOOK_URL environment variable is required")
        logger.info("💡 Set it like: export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/your/webhook/url'")
        sys.exit(1)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create HTTP server
        server = HTTPServer((HOST, PORT), WebhookHandler)
        
        logger.info(f"🚀 Starting webhook server on http://{HOST}:{PORT}")
        logger.info(f"📡 Discord webhook configured: {discord_webhook_url}")
        logger.info(f"💡 Send POST requests to: http://{HOST}:{PORT}/webhook")
        logger.info(f"🏥 Health check available at: http://{HOST}:{PORT}/health")
        logger.info(f"🛑 Press Ctrl+C to stop the server")
        
        # Start the server
        server.serve_forever()
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"❌ Port {PORT} is already in use. Try a different port:")
            logger.info(f"💡 export WEBHOOK_PORT=8081")
        else:
            logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
