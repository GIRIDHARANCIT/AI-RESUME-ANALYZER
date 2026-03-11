FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r ./backend/requirements.txt

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
