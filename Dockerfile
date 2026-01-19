FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "main.py"]
