#!/usr/bin/env python3
"""
Simple database setup script - creates all tables directly.
Save this as: backend/simple_db_setup.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def setup_database():
    """Create all database tables directly."""

    print("Setting up database...")

    # Remove existing database
    db_file = backend_dir / "app.db"
    if db_file.exists():
        print(f"Removing existing database: {db_file}")
        db_file.unlink()

    try:
        # Import after path setup
        from app.core.database import engine
        from app.models.base import TimeStampedBase
        from app.models.website import Website
        from app.models.page import Page
        from app.models.chunk import Chunk
        from app.models.conversation import Conversation
        from app.models.message import Message
        from app.models.user import User

        print("Creating all tables...")
        TimeStampedBase.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

        # Test the connection
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            # Simple query to test
            result = db.execute("SELECT 1").fetchone()
            print("✅ Database connection test successful!")
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


if __name__ == "__main__":
    setup_database()