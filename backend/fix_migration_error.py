#!/usr/bin/env python3
"""
Script to clean the database and run migrations properly.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def clean_and_migrate():
    """Clean the database and run migrations."""

    # Step 1: Remove the SQLite database file
    db_file = backend_dir / "app.db"
    if db_file.exists():
        print(f"Removing existing database: {db_file}")
        db_file.unlink()

    # Step 2: Remove migration files that are causing issues
    versions_dir = backend_dir / "alembic" / "versions"

    problem_files = [
        "f1d4a814e6ed_add_pages_table.py",  # This one is causing the issue
    ]

    for problem_file in problem_files:
        file_path = versions_dir / problem_file
        if file_path.exists():
            print(f"Removing problematic migration: {file_path}")
            file_path.unlink()

    # Step 3: Run migrations
    print("Running migrations...")
    os.chdir(backend_dir)

    import alembic.config

    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]

    try:
        alembic.config.main(argv=alembic_args)
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    clean_and_migrate()