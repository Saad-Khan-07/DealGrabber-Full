# Use latest Python with better compatibility
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip chromium \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome path
ENV CHROME_BIN=/usr/bin/chromium

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Pre-download ChromeDriver matching the Chrome version
RUN python -c "from webdriver_manager.chrome import ChromeDriverManager; import os; chrome_binary = os.environ.get('CHROME_BIN', '/usr/bin/chromium'); version = os.popen(f'{chrome_binary} --version').read().split()[1].split('.')[0] if os.path.exists(chrome_binary) else None; ChromeDriverManager(chrome_version=version).install() if version else ChromeDriverManager().install()"

# Expose Railway-assigned port
EXPOSE $PORT

# Start Gunicorn server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "dealgrabberflask.app:app"]