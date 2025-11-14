"""
Database initialization script.
Creates all tables if they don't exist.
"""

import sys
from app.database import init_db, engine
from app.config import settings

def main():
    """Initialize database tables."""
    print(f"Initializing database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    try:
        init_db()
        print("✅ Database tables created successfully!")
        return 0
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

