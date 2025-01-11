# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt (or equivalent) to the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . .

# Load environment variables from a .env file
RUN pip install python-dotenv

# Expose a port if required (optional, for debugging purposes)
EXPOSE 8000

# Command to run the bot
CMD ["python", "main.py"]
