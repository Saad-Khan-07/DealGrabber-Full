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

# Install Chrome 114 from an archived source
RUN wget -O /tmp/google-chrome.deb https://cdn.aykutsevinc.com/google-chrome/google-chrome-stable_114.0.5735.90-1_amd64.deb && \
    apt-get update && apt-get install -y /tmp/google-chrome.deb && \
    rm /tmp/google-chrome.deb

# Install ChromeDriver 114
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

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
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]
