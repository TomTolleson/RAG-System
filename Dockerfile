FROM python:3.13-slim

WORKDIR /app

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements if you have them
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Copy the rest of your application
COPY . .

# Your CMD or other instructions here 