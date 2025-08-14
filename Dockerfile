# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r webhook && useradd -r -g webhook webhook

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY webhook.py .

# Change ownership to non-root user
RUN chown -R webhook:webhook /app

# Switch to non-root user
USER webhook

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=120s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${WEBHOOK_PORT}/health')"

# Set environment variables with defaults
ENV WEBHOOK_HOST=0.0.0.0
ENV WEBHOOK_PORT=5031

# Run the application
CMD ["python", "webhook.py"]
