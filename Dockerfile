FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ODBC
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    lsb-release \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver for SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port for FastMCP HTTP streaming
EXPOSE 8000

# Set environment variables for FastMCP 2.9.2+ HTTP
ENV PYTHONPATH=/app
ENV MCP_HTTP_HOST=0.0.0.0
ENV MCP_HTTP_PORT=8000
ENV MCP_API_PATH=/mcp
ENV LOG_LEVEL=DEBUG

# Run the server
CMD ["python", "src/server.py"]
