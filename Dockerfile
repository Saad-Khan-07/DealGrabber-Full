# Use latest Python with better compatibility
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome and ChromeDriver paths
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose Railway-assigned port
EXPOSE $PORT

# Start Gunicorn server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]
