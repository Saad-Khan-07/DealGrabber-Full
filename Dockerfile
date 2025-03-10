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
    xdg-utils \
    chromium \
    chromium-driver

# Set environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Upgrade pip safely
RUN pip install --upgrade pip

# Install dependencies (excluding WebDriver Manager)
RUN pip install --no-cache-dir -r requirements.txt

# Expose Railway-assigned port
EXPOSE $PORT

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]