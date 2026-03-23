#!/bin/sh

# Entrypoint script to be executed in a container: Migrate SQL schema, and run the web backed on success.

set -e

echo "Migrating database..."
uv run alembic upgrade head

echo "Starting web app..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
