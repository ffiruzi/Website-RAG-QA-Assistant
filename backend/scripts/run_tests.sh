#!/bin/bash
set -e

cd "$(dirname "$0")/.."

# Run unit tests
PYTHONPATH=. pytest -xvs tests/

# Run with coverage reporting
if [ "$1" = "--coverage" ]; then
    PYTHONPATH=. pytest --cov=app --cov-report=term --cov-report=html tests/
    echo "Coverage report generated to htmlcov/index.html"
fi