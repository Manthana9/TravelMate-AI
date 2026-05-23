# Use the official lightweight Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage Docker caching
COPY backend/requirements.txt ./backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the entire project code into the container
COPY . .

# Expose the port Cloud Run will listen on
EXPOSE 8080

# Run the Flask server from the root execution context
CMD ["python", "backend/app.py"]