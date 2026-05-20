#!/bin/bash
# Database migration script

set -e

echo "Running database migrations..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h postgres -p 5432; do
  sleep 1
done

echo "Database is ready!"

# Run migrations
cd /app
python -m alembic upgrade head

echo "Migrations completed successfully!"
