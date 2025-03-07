# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Ensure latest ChromeDriver version matches installed Chromium
RUN CHROMIUM_VERSION=$(chromium --version | awk '{print $2}') && \
    LATEST_CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROMIUM_VERSION/linux64/chromedriver-linux64.zip" && \
    wget -O chromedriver.zip "$LATEST_CHROMEDRIVER_URL" && \
    unzip chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver.zip

# Set environment variables for Selenium
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

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]
