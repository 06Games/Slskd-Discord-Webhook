"""
HTTP server for handling webhook requests.
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler

from discord_client import send_to_discord_webhook

logger = logging.getLogger(__name__)


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for incoming webhooks."""
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_POST(self):
        """Handle POST requests (webhook calls)."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the POST data
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                logger.info(f"📦 Received webhook data: {json_data.get('type', 'Unknown type')}")
                logger.debug(json.dumps(json_data))
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON received: {e}")
                self.send_error(400, "Invalid JSON")
                return
            
            # Send to Discord
            discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            if not discord_webhook_url:
                logger.error("❌ DISCORD_WEBHOOK_URL environment variable not set")
                self.send_error(500, "Discord webhook URL not configured")
                return
            
            success = send_to_discord_webhook(discord_webhook_url, json_data)
            
            if success:
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Webhook processed successfully"}
                self.wfile.write(json.dumps(response).encode())
                logger.info("✅ Webhook processed successfully")
            else:
                self.send_error(500, "Failed to send to Discord")
                
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "Discord Webhook Relay",
                "endpoints": {
                    "webhook": "POST /webhook",
                    "health": "GET /health"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            logger.info("🏥 Health check requested")
        else:
            self.send_error(404, "Not Found")
