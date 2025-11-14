# Dockerfile for FaceStream Backend
# Optimized for Railway deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for face recognition
# Required for compiling dlib and face-recognition packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    python3-pip \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

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
    email-validator>=2.0.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-dateutil==2.8.2 \
    redis>=5.0.0 \
    hiredis>=2.2.3 \
    numpy==1.24.3 \
    Pillow==10.1.0

# Copy requirements.txt for reference
COPY requirements.txt .

# Install face recognition dependencies
# These packages take 15-20+ minutes to compile but are required for live video recognition
# Install them separately to catch errors early
RUN echo "==========================================" && \
    echo "Installing face recognition packages..." && \
    echo "This may take 15-20 minutes (especially dlib)" && \
    echo "=========================================="

# Install opencv-python first (moderate size)
RUN echo "Installing opencv-python..." && \
    pip install --no-cache-dir opencv-python==4.8.1.78 && \
    echo "✓ opencv-python installed"

# Install dlib (this is the slowest - 10-15 minutes)
# dlib requires cmake and build tools (already installed above)
# Fix CMake compatibility: dlib 19.24.2 uses old pybind11 with incompatible CMake syntax
# Solution: Patch pybind11 CMakeLists.txt to require CMake 3.10+ instead of 3.5
ENV DLIB_USE_CUDA=0
ENV DLIB_USE_BLAS=1

# Download dlib source
RUN echo "Downloading dlib source..." && \
    pip download --no-deps --no-binary :all: dlib==19.24.2

# Extract and patch dlib
RUN DLIB_TAR=$(ls dlib-*.tar.gz | head -1) && \
    echo "Extracting $DLIB_TAR..." && \
    tar -xzf "$DLIB_TAR" && \
    DLIB_DIR=$(ls -d dlib-* | head -1) && \
    echo "Patching pybind11 CMakeLists.txt for CMake compatibility..." && \
    find "$DLIB_DIR" -name "CMakeLists.txt" -path "*/pybind11/*" -exec sed -i 's/cmake_minimum_required(VERSION 3.5)/cmake_minimum_required(VERSION 3.10)/' {} \; && \
    echo "✓ Patch applied" && \
    rm -f "$DLIB_TAR"

# Install patched dlib
RUN echo "Installing dlib (this will take 10-15 minutes)..." && \
    echo "Using BLAS for faster compilation..." && \
    DLIB_DIR=$(ls -d dlib-* | head -1) && \
    pip install --no-cache-dir --no-build-isolation "$DLIB_DIR" && \
    rm -rf "$DLIB_DIR" && \
    echo "✓ dlib installed successfully"

# Install face-recognition last (depends on dlib)
RUN echo "Installing face-recognition..." && \
    pip install --no-cache-dir face-recognition==1.3.0 && \
    echo "✓ face-recognition installed"

RUN echo "==========================================" && \
    echo "✓ All face recognition packages installed!" && \
    echo "=========================================="

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8000}

# Run migrations and start server
# Railway sets PORT environment variable automatically
CMD ["/app/start.sh"]

