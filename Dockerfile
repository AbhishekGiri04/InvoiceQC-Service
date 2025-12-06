# Dockerfile for Invoice QC Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY invoice_qc/ ./invoice_qc/
COPY pdfs/ ./pdfs/

# Create directories for outputs
RUN mkdir -p extracted reports

# Expose port for API
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "invoice_qc.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
