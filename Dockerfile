# Use the official Microsoft Playwright Python image (which has all OS dependencies built-in)
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install only Chromium browser (OS dependencies are already handled by the base image)
RUN playwright install chromium

# Copy all the rest of the project files
COPY . .

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
