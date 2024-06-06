# Use the official Python image from Docker Hub
FROM python:3.9
ENV PYTHONUNBUFFERED=1
RUN apt-get update && pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy the local requirements.txt to the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 8000
ENV FLASK_RUN_HOST 0.0.0.0

# Expose the Flask application port
EXPOSE 8000

# Set the default command to run when the container starts
CMD  ["python", "src/app.py"]
