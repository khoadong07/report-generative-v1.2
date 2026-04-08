# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for weasyprint (PDF generation)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Streamlit and weasyprint for PDF export
RUN pip install --no-cache-dir \
    streamlit==1.31.0 \
    weasyprint==60.2

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose Streamlit port
EXPOSE 13333

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=13333
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:13333/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "app_template_html.py", "--server.port=13333", "--server.address=0.0.0.0"]
