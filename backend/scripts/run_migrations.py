import os
import sys
import alembic.config


def run_migrations():
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]

    # Change to the directory where alembic.ini is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

    # Run the migrations
    alembic.config.main(argv=alembic_args)


if __name__ == "__main__":
    run_migrations()