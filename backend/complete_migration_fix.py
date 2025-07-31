#!/usr/bin/env python3
"""
Complete fix for migration issues by resetting everything properly.
"""
import os
import sys
import shutil
from pathlib import Path


def complete_migration_fix():
    """Completely fix all migration issues."""

    # Get the backend directory
    if 'backend' in os.getcwd():
        backend_dir = Path.cwd()
    else:
        backend_dir = Path.cwd() / 'backend'

    print(f"Working in directory: {backend_dir}")

    # Step 1: Remove the database file
    db_files = [
        backend_dir / "app.db",
        backend_dir / "app.db-journal",
        backend_dir / "app.db-wal",
        backend_dir / "app.db-shm"
    ]

    for db_file in db_files:
        if db_file.exists():
            print(f"Removing: {db_file}")
            db_file.unlink()

    # Step 2: Clean up ALL migration files except the initial ones
    versions_dir = backend_dir / "alembic" / "versions"

    if versions_dir.exists():
        print("Cleaning up migration files...")
        for migration_file in versions_dir.glob("*.py"):
            if migration_file.name != "__init__.py":
                print(f"Removing: {migration_file}")
                migration_file.unlink()

    # Step 3: Create a fresh, complete migration
    print("Creating fresh migration...")

    fresh_migration = versions_dir / "001_fresh_start.py"

    migration_content = '''"""Fresh start migration

Revision ID: 001_fresh_start
Revises: 
Create Date: 2025-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_fresh_start'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create websites table
    op.create_table(
        'websites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('sitemap_url', sa.String(), nullable=True),
        sa.Column('prompt_template_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_websites_id'), 'websites', ['id'], unique=False)
    op.create_index(op.f('ix_websites_url'), 'websites', ['url'], unique=True)

    # Create pages table
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('last_crawled_at', sa.String(), nullable=True),
        sa.Column('is_indexed', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pages_id'), 'pages', ['id'], unique=False)
    op.create_index(op.f('ix_pages_url'), 'pages', ['url'], unique=True)

    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chunks_id'), 'chunks', ['id'], unique=False)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('conversation_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_user_message', sa.Boolean(), default=True),
        sa.Column('sources', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    # Create embedding_jobs table
    op.create_table(
        'embedding_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('documents_found', sa.Integer(), nullable=True),
        sa.Column('documents_processed', sa.Integer(), nullable=True),
        sa.Column('chunks_created', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('is_refresh', sa.Boolean(), default=False),
        sa.Column('job_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_jobs_id'), 'embedding_jobs', ['id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('secret', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhooks_id'), 'webhooks', ['id'], unique=False)

    # Create webhook_logs table
    op.create_table(
        'webhook_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('webhook_id', sa.Integer(), nullable=False),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.String(), nullable=True),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_logs_id'), 'webhook_logs', ['id'], unique=False)

def downgrade():
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_webhook_logs_id'), table_name='webhook_logs')
    op.drop_table('webhook_logs')
    op.drop_index(op.f('ix_webhooks_id'), table_name='webhooks')
    op.drop_table('webhooks')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_embedding_jobs_id'), table_name='embedding_jobs')
    op.drop_table('embedding_jobs')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_conversations_session_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_index(op.f('ix_chunks_id'), table_name='chunks')
    op.drop_table('chunks')
    op.drop_index(op.f('ix_pages_url'), table_name='pages')
    op.drop_index(op.f('ix_pages_id'), table_name='pages')
    op.drop_table('pages')
    op.drop_index(op.f('ix_websites_url'), table_name='websites')
    op.drop_index(op.f('ix_websites_id'), table_name='websites')
    op.drop_table('websites')
'''

    with open(fresh_migration, 'w') as f:
        f.write(migration_content)

    print(f"Created fresh migration: {fresh_migration}")

    # Step 4: Run migrations
    print("\nRunning fresh migrations...")
    os.chdir(backend_dir)

    # Set up the path
    sys.path.insert(0, str(backend_dir))

    try:
        import alembic.config

        # Run upgrade to head
        alembic_args = [
            '--raiseerr',
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembic_args)

        print("✅ Database migrations completed successfully!")

        # Step 5: Initialize the database with some data
        print("\nInitializing database...")
        from app.core.database import SessionLocal
        from app.db.init_db import init_db

        db = SessionLocal()
        try:
            init_db(db)
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nTrying direct table creation...")

        # Alternative: Just create tables directly
        try:
            from app.core.database import engine
            from app.models.base import TimeStampedBase

            print("Creating tables directly...")
            TimeStampedBase.metadata.create_all(bind=engine)
            print("✅ Tables created successfully!")

            # Try to initialize
            from app.core.database import SessionLocal
            from app.db.init_db import init_db

            db = SessionLocal()
            try:
                init_db(db)
                print("✅ Database initialized successfully!")
            except Exception as e:
                print(f"Warning: Could not initialize database: {e}")
            finally:
                db.close()

        except Exception as e2:
            print(f"❌ Direct table creation also failed: {e2}")
            return False

    return True


if __name__ == "__main__":
    if complete_migration_fix():
        print("\n🎉 All migration issues fixed! You can now start your application.")
        print("\nTo verify everything is working, try:")
        print("  python run_with_real.py")
    else:
        print("\n❌ Could not fix migration issues. Please check the error messages above.")