import os
import sys
import alembic.config
import argparse


def create_migration(message):
    # Get the absolute path to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change to the backend directory
    os.chdir(backend_dir)

    alembic_args = [
        '--raiseerr',
        'revision', '--autogenerate',
        '-m', message,
    ]

    # Run the migration
    alembic.config.main(argv=alembic_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new Alembic migration')
    parser.add_argument('message', help='Migration message')
    args = parser.parse_args()

    create_migration(args.message)