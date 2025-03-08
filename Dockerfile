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
    libwayland-client0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils

# ✅ Install Google Chrome (Stable)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable

# ✅ Install ChromeDriver (Matching Chrome Version)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    wget -q -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL" && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# ✅ Set environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# ✅ Upgrade pip safely
RUN pip install --upgrade pip 

# ✅ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Railway-assigned port
EXPOSE $PORT

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]
