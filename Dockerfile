FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Weasyprint system libraries cleanly
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    weasyprint \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining project files
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]