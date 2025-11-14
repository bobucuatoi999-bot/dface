# Dockerfile for FaceStream Backend
# Optimized for Railway deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (optional - for face recognition if needed)
# Note: These are large and may not be needed for auth-only deployments
# Uncomment if you need face recognition features
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     cmake \
#     libopenblas-dev \
#     liblapack-dev \
#     libx11-dev \
#     libgtk-3-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: face-recognition and dlib may fail to install - that's OK, app handles it gracefully
RUN pip install --no-cache-dir -r requirements.txt || true

# Install core dependencies separately to ensure they work
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    websockets==12.0 \
    python-multipart==0.0.6 \
    sqlalchemy==2.0.23 \
    psycopg2-binary>=2.9.9 \
    alembic==1.12.1 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    numpy==1.24.3 \
    Pillow==10.1.0 \
    python-dateutil==2.8.2

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8000}

# Run migrations and start server
# Railway sets PORT environment variable automatically
CMD ["/app/start.sh"]

