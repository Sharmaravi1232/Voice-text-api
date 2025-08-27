# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential ffmpeg git

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 7860

# Run FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
