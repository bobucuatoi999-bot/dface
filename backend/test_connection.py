"""
Simple script to test database connection and models.
Run this to verify your database setup is correct.
"""

import sys
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import User, FaceEmbedding, RecognitionLog
from app.config import settings

def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
        print(f"[OK] Connected to PostgreSQL: {version}")
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print(f"   Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
        return False

def test_models():
    """Test that models can be imported and tables exist."""
    print("\nTesting database models...")
    try:
        db = SessionLocal()
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["users", "face_embeddings", "recognition_logs"]
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f"[WARNING] Missing tables: {missing_tables}")
            print("   Run: python init_db.py or alembic upgrade head")
            return False
        else:
            print(f"[OK] All tables exist: {tables}")
        
        # Test query
        user_count = db.query(User).count()
        print(f"[OK] User model works. Current users: {user_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"[ERROR] Model test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("FaceStream Backend - Connection Test")
    print("=" * 50)
    
    connection_ok = test_connection()
    models_ok = test_models() if connection_ok else False
    
    print("\n" + "=" * 50)
    if connection_ok and models_ok:
        print("[SUCCESS] All tests passed! Backend is ready.")
        return 0
    else:
        print("[INFO] Some tests failed. PostgreSQL may not be running.")
        print("       The server can still start, but database features won't work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

