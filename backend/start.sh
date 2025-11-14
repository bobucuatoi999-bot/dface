#!/bin/sh
# Startup script for Railway deployment
# Checks for required environment variables before starting

# Don't exit on error immediately - we want to log errors first
set +e

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
    sleep 10
    exit 1
fi

echo "✓ DATABASE_URL is configured"
echo ""

# Run database migrations (allow to fail gracefully)
echo "Running database migrations..."
MIGRATION_OUTPUT=$(alembic upgrade head 2>&1)
MIGRATION_EXIT_CODE=$?

if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
    echo "✓ Database migrations completed successfully"
else
    echo "⚠ WARNING: Database migrations failed (exit code: $MIGRATION_EXIT_CODE)"
    echo "Migration output:"
    echo "$MIGRATION_OUTPUT"
    echo ""
    echo "If you see 'could not translate host name' error:"
    echo "  → Your DATABASE_URL might be using internal Railway hostname"
    echo "  → Try using DATABASE_PUBLIC_URL instead (from Postgres Variables)"
    echo ""
    echo "The application will still attempt to start."
fi
echo ""

# Start the application
echo "Starting uvicorn server on port ${PORT:-8000}..."
echo "=========================================="
echo ""

# Check if Python can import the app
echo "Verifying application can be imported..."
if python -c "import app.main" 2>&1; then
    echo "✓ Application import successful"
else
    IMPORT_ERROR=$(python -c "import app.main" 2>&1)
    echo "❌ ERROR: Failed to import application"
    echo "Error details:"
    echo "$IMPORT_ERROR"
    echo ""
    echo "This usually means:"
    echo "  - Missing Python dependencies"
    echo "  - Syntax error in code"
    echo "  - Import error in modules"
    echo ""
    echo "Attempting to start anyway (errors will be shown in uvicorn logs)..."
fi
echo ""

# Auto-create admin user if none exists (don't fail if this errors)
echo "Checking for admin user..."
if python auto_create_admin.py 2>&1; then
    echo "✓ Admin check completed"
else
    echo "⚠️  Could not check/create admin user (non-critical - continuing startup)"
fi
echo ""

# Start uvicorn with error handling
echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio --log-level info

