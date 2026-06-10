# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Render uses (typically 10000)
EXPOSE 10000

# Run the Flask application using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
