# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any system dependencies and dependencies from requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends pkg-config libmariadb-dev gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables for Django
ENV PYTHONUNBUFFERED=1

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "ML_CS_Pro_Backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

