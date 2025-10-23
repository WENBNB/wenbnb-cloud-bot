# =========================================================
# 🧠 WENBNB Neural Engine v5.5 — Render Optimized Build
# =========================================================

# Base image (lightweight, secure & fast)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . /app

# Prevent Python from writing .pyc files and enable logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose default Render port
EXPOSE 8080

# Default startup command
CMD gunicorn wenbot:app --bind 0.0.0.0:8080 --timeout 120 --log-level info
