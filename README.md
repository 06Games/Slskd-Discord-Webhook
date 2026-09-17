# Slskd Discord Webhook

A lightweight webhook relay that receives event notifications from [slskd](https://github.com/slskd/slskd) and formats them into Discord embeds.

## Features

- 💬 **Chat Messages**: Formats private and room messages (ignores message replays)
- 📁 **Transfers**: Notifies on completed uploads, file downloads, and directory downloads (including size, speed, and duration)
- 🔌 **Connection Status**: Notifies when the Soulseek client connects or disconnects, including disconnect reasons
- 🔔 **User Pings**: Optionally mentions your Discord user ID when a private or room message arrives
- 🔗 **Web UI Links**: Links directly to your slskd instance or chat if configured

## Quick Start

### Docker

```bash
docker run -d \
  --name slskd-discord-webhook \
  -p 5031:5031 \
  -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
  -e SLSKD_URL="http://your-slskd-host:5030" \
  slskd-discord-webhook
```

Or using `docker-compose.yml`:

```yaml
services:
  discord-webhook:
    build: .
    container_name: slskd-discord-webhook
    ports:
      - "5031:5031"
    environment:
      - DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
      - SLSKD_URL=http://slskd:5030
      # - DISCORD_PING_USER_ID=123456789012345678
    restart: unless-stopped
```

### Python

```bash
pip install -r requirements.txt
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python webhook.py
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_WEBHOOK_URL` | Yes | — | Discord channel webhook URL |
| `SLSKD_URL` | No | — | Base URL of your slskd instance (enables direct links in embeds) |
| `DISCORD_PING_USER_ID` | No | — | Discord user ID to mention when room/private messages are received |
| `WEBHOOK_PORT` | No | `8080` (`5031` in Docker) | Port the relay server listens on |
| `WEBHOOK_HOST` | No | `0.0.0.0` | Host interface to bind to |

## Slskd Configuration

Point your slskd webhook settings to the relay's webhook endpoint:

```yaml
integrations:
  webhooks:
    discord:
      on:
        - Any
      call:
        url: http://<relay-host>:<port>/webhook
```

A health check endpoint is also available at `GET /health`.
