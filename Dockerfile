# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app/backend

# Copy backend code
COPY backend/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional)
EXPOSE 8000

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
