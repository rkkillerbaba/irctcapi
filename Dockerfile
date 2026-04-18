# Use official Python lightweight image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser (Chromium) and its necessary system dependencies
RUN playwright install --with-deps chromium

# Copy all the rest of the project files
COPY . .

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
