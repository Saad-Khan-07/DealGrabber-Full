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

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Install ChromeDriver using npm and puppeteer
RUN apt-get install -y nodejs npm && \
    npm install puppeteer && \
    cp node_modules/puppeteer/.local-chromium/*/chrome-linux*/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/google-chrome

# Copy application
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "run.py"]