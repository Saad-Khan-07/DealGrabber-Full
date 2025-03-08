FROM python:3.10

# Install Chrome and necessary utilities
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    curl \
    ca-certificates

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Install specific ChromeDriver version
RUN wget -q "https://chromedriver.storage.googleapis.com/122.0.6261.94/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Verify installation
RUN google-chrome --version && chromedriver --version

# Set environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# Copy application
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "run.py"]