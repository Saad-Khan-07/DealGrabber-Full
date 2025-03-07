# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (including Chrome & ChromeDriver)
RUN apt-get update && apt-get install -y \
    curl wget unzip \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver 134 (which matches Chrome 134)
RUN wget -O /usr/bin/chromedriver https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.35/linux64/chromedriver-linux64.zip \
    && chmod +x /usr/bin/chromedriver

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

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]
