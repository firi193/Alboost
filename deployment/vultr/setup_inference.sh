#!/bin/bash

# Exit on error
set -e

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone or pull repository
if [ -d "/home/ubuntu/marketing-ai-agent" ]; then
    cd /home/ubuntu/marketing-ai-agent
    git pull
else
    git clone https://github.com/yourusername/marketing-ai-agent.git /home/ubuntu/marketing-ai-agent
    cd /home/ubuntu/marketing-ai-agent
fi

# Build and run Docker container
sudo docker build -t marketing-ai-agent:v1 -f deployment/vultr/Dockerfile .
sudo docker run -d --name marketing-ai-agent --restart unless-stopped -p 8000:8000 marketing-ai-agent:v1

# Set up PostgreSQL
if ! sudo docker ps | grep -q "postgres"; then
    echo "Setting up PostgreSQL..."
    sudo docker run -d --name postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 postgres:15
fi

# Download LLaMA 3 model
if [ ! -d "/home/ubuntu/models" ]; then
    echo "Downloading LLaMA 3 model..."
    mkdir -p /home/ubuntu/models
    cd /home/ubuntu/models
    # Add your model download commands here
    # wget https://example.com/llama3-model.zip
    # unzip llama3-model.zip
fi

# Start services
sudo docker start postgres
sudo docker start marketing-ai-agent

# Wait for services to start
sleep 5

# Verify services are running
echo "Checking service status..."
if sudo docker ps | grep -q "postgres" && sudo docker ps | grep -q "marketing-ai-agent"; then
    echo "All services started successfully!"
else
    echo "Error: Some services failed to start"
    exit 1
fi

# Print API endpoint
echo "API is running at: http://$(curl -s ifconfig.me):8000"

# Keep script running (for debugging)
while true; do sleep 3600; done