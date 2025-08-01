FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY workflows/vultr_inference_api.py ./vultr_inference_api.py
COPY workflows/lambda_handlers/ ./lambda_handlers/

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "lambda_handlers.campaign_trigger:app", "--host", "0.0.0.0", "--port", "8000"]