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

# Install core dependencies first (fast, required for app to run)
# This ensures the app can start quickly even if optional packages fail
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
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
    python-dateutil==2.8.2 \
    redis>=5.0.0 \
    hiredis>=2.2.3 \
    numpy==1.24.3 \
    Pillow==10.1.0

# Copy requirements.txt for reference
COPY requirements.txt .

# Skip face recognition dependencies for faster builds
# These packages (opencv-python, face-recognition, dlib) take 15-20+ minutes to compile
# The app handles missing face recognition gracefully and runs in auth-only mode
# To enable face recognition later, uncomment the line below:
# RUN pip install --no-cache-dir opencv-python==4.8.1.78 face-recognition==1.3.0 dlib==19.24.2 || true

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8000}

# Run migrations and start server
# Railway sets PORT environment variable automatically
CMD ["/app/start.sh"]

