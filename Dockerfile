FROM python:3.10-slim

# Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libdrm2 \
    libwayland-client0

# Fix distutils issue
RUN rm -rf /usr/lib/python3/dist-packages/distutils-precedence.pth

# Install Chrome and ChromeDriver properly
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb && \
    apt-get install -y chromium-driver

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Upgrade pip without permission issues
RUN python -m pip install --upgrade pip --break-system-packages

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Railway-assigned port
EXPOSE $PORT

# Run the application
CMD ["python", "run.py"]
