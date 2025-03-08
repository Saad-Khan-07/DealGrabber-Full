FROM selenium/standalone-chrome:latest

# Install Python 3.10
RUN sudo apt-get update && \
    sudo apt-get install -y software-properties-common && \
    sudo add-apt-repository ppa:deadsnakes/ppa && \
    sudo apt-get update && \
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Make Python 3.10 the default python
RUN sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Update pip
RUN python -m pip install --upgrade pip

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy application
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "run.py"]