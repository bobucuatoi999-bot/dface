#!/bin/sh
# Startup script for Railway deployment
# Checks for required environment variables before starting

set -e

echo "=========================================="
echo "FaceStream Backend - Starting..."
echo "=========================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo ""
    echo "=========================================="
    echo "ERROR: DATABASE_URL environment variable is not set!"
    echo "=========================================="
    echo ""
    echo "The application requires a PostgreSQL database to run."
    echo ""
    echo "HOW TO FIX:"
    echo "1. Go to Railway Dashboard"
    echo "2. Select your project"
    echo "3. Click 'New' → 'Database' → 'Add PostgreSQL'"
    echo "4. Railway will automatically inject DATABASE_URL into your backend service"
    echo ""
    echo "OR manually set in Railway Variables:"
    echo "   DATABASE_URL=\${{Postgres.DATABASE_URL}}"
    echo ""
    echo "After setting DATABASE_URL, Railway will automatically redeploy."
    echo ""
    echo "Container will exit (no restart loop)."
    echo "Fix: Add PostgreSQL database in Railway Dashboard, then redeploy."
    exit 1
fi

echo "✓ DATABASE_URL is configured"
echo ""

# Run database migrations (allow to fail gracefully)
echo "Running database migrations..."
if alembic upgrade head; then
    echo "✓ Database migrations completed successfully"
else
    echo "⚠ WARNING: Database migrations failed or skipped"
    echo "  This might be OK if:"
    echo "  - Database is not ready yet"
    echo "  - Migrations have already been applied"
    echo "  The application will still attempt to start."
fi
echo ""

# Start the application
echo "Starting uvicorn server on port ${PORT:-8000}..."
echo "=========================================="
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio

