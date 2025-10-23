# ============================================================
#   WENBNB Neural Engine v5.5 - Dockerfile (Render Compatible)
# ============================================================

FROM python:3.11-slim

# Work directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Render port
ENV PORT=10000
EXPOSE 10000

# Health check (Render-style)
HEALTHCHECK CMD curl --fail http://localhost:10000/ping || exit 1

# Default command
CMD ["python", "wenbot.py"]
