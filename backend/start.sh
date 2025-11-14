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
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ❌ DATABASE_URL MISSING - ACTION REQUIRED                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "The application requires a PostgreSQL database to run."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 STEP-BY-STEP FIX:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "METHOD 1 (Easiest - Recommended):"
    echo "  1. Go to Railway Dashboard → Your Project"
    echo "  2. Click 'New' → 'Database' → 'Add PostgreSQL'"
    echo "  3. Railway will auto-inject DATABASE_URL and redeploy"
    echo ""
    echo "METHOD 2 (If PostgreSQL already exists):"
    echo "  1. Railway Dashboard → Backend Service → Variables"
    echo "  2. Add new variable:"
    echo "     Name:  DATABASE_URL"
    echo "     Value: \${{Postgres.DATABASE_URL}}"
    echo "     (Replace 'Postgres' with your actual PostgreSQL service name)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📖 See RAILWAY_POSTGRESQL_SETUP.md for detailed instructions"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Container will exit. This is EXPECTED until DATABASE_URL is set."
    echo "After adding PostgreSQL, Railway will automatically redeploy."
    echo ""
    sleep 5
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

