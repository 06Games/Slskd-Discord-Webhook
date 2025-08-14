import os
import json
import requests
import sys
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
                logger.debug(json.dumps(data))
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON received: {e}")
                self.send_error(400, "Invalid JSON")
                return
            finally:
            
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

def format_slskd_to_discord(data: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Format Slskd notification data into Discord webhook format.
    
    Args:
        data: Raw Slskd notification data
        
    Returns:
        Formatted Discord webhook payload
    """

    SLSKD_URL = os.getenv('SLSKD_URL')
    SLSKD_ICO = f"{SLSKD_URL}/favicon.ico" if SLSKD_URL else None

    # Base Discord webhook structure
    webhook_payload = {
        "username": "Slskd",
        "avatar_url": SLSKD_ICO
    }
    
    message_type = data.get("type", "Unknown")
    timestamp = data.get("timestamp", "")
    
    # Format based on message type
    if message_type == "RoomMessageReceived":
        data = data.get("message")

        if data.get("wasReplayed", False):
            webhook_payload = None # Ignore message
        username = data.get("username", "Unknown User")
        room_name = data.get("roomName", "Unknown Room")
        timestamp = data.get("timestamp", "")
        message = data.get("message", "")
        
        # Set color based on blacklist status
        color = 15158332 if blacklisted else 5793266  # Red if blacklisted, blue otherwise
        
        webhook_payload.update({
            "content": "💬 You've received a room message",
            "embeds": [{
                "color": color,
                "author": {
                    "name": username
                },
                "description": message,
                "footer": {
                    "text": f"in #{room_name}"
                },
                "timestamp": timestamp
            }]
        })
    
    elif message_type == "PrivateMessageReceived":
        data = data.get("message")

        if data.get("wasReplayed", False):
            webhook_payload = None # Ignore message
        username = data.get("username", "Unknown User")
        timestamp = data.get("timestamp", "")
        message = data.get("message", "")
        
        webhook_payload.update({
            "content": "📩 You've received a private message",
            "embeds": [{
                "color": 3447003,  # Blue color for private messages
                "author": {
                    "name": username
                },
                "description": message,
                "footer": {
                    "text": "Private Message"
                },
                "timestamp": timestamp
            }]
        })
    
#     elif message_type == "UserJoined":
#         username = data.get("username", "Unknown User")
#         room_name = data.get("roomName", "Unknown Room")
#
#         webhook_payload.update({
#             "content": "👋 User joined a room",
#             "embeds": [{
#                 "color": 3066993,  # Green color for joins
#                 "author": {
#                     "name": username
#                 },
#                 "description": f"Joined the room",
#                 "footer": {
#                     "text": f"in #{room_name}"
#                 },
#                 "timestamp": timestamp
#             }]
#         })
#
#     elif message_type == "UserLeft":
#         username = data.get("username", "Unknown User")
#         room_name = data.get("roomName", "Unknown Room")
#
#         webhook_payload.update({
#             "content": "👋 User left a room",
#             "embeds": [{
#                 "color": 15105570,  # Orange color for leaves
#                 "author": {
#                     "name": username
#                 },
#                 "description": f"Left the room",
#                 "footer": {
#                     "text": f"in #{room_name}"
#                 },
#                 "timestamp": timestamp
#             }]
#         })
#
#     elif message_type == "TransferCompleted":
#         username = data.get("username", "Unknown User")
#         filename = data.get("filename", "Unknown File")
#         direction = data.get("direction", "unknown")  # "Upload" or "Download"
#
#         emoji = "⬆️" if direction.lower() == "upload" else "⬇️"
#         color = 3066993 if direction.lower() == "upload" else 3447003
#
#         webhook_payload.update({
#             "content": f"{emoji} Transfer completed",
#             "embeds": [{
#                 "color": color,
#                 "author": {
#                     "name": username
#                 },
#                 "description": f"**{filename}**",
#                 "footer": {
#                     "text": f"{direction} completed"
#                 },
#                 "timestamp": timestamp
#             }]
#         })
#
#     elif message_type == "SearchRequested":
#         username = data.get("username", "Unknown User")
#         query = data.get("query", "")
#
#         webhook_payload.update({
#             "content": "🔍 Search request received",
#             "embeds": [{
#                 "color": 10181046,  # Purple color for searches
#                 "author": {
#                     "name": username
#                 },
#                 "description": f"Searched for: **{query}**",
#                 "footer": {
#                     "text": "Search Request"
#                 },
#                 "timestamp": timestamp
#             }]
#         })
    
    else:
        # Generic format for unknown message types
        webhook_payload.update({
            "content": f"📢 Slskd Notification: {message_type}",
            "embeds": [{
                "color": 9807270,  # Gray color for unknown types
                "title": message_type,
                "description": f"```json\n{json.dumps(data, indent=2)}\n```",
                "footer": {
                    "text": "Raw notification data"
                },
                "timestamp": timestamp
            }]
        })
    
    return webhook_payload

def send_to_discord_webhook(webhook_url: str, data: Dict[Any, Any]) -> bool:
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
            logger.info(f"🎨 Ignored Slskd '{data.get('type')}' notification")
            return True

        logger.info(f"🎨 Formatted Slskd '{data.get('type')}' notification for Discord")
        logger.debug(json.dumps(webhook_payload))
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        logger.info(f"✅ Successfully sent data to Discord webhook (Status: {response.status_code})")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error sending to Discord webhook: {e}\n{e.response.text}")
        return False

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
        logger.info(f"📡 Discord webhook configured: {discord_webhook_url[:50]}...")
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
