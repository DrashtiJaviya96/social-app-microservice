#!/bin/sh

# Print which database we are waiting for
echo "Waiting for PostgreSQL at $POST_DB_HOST:$POST_DB_PORT ..."

# Wait until PostgreSQL is ready
while ! nc -z $POST_DB_HOST $POST_DB_PORT; do
  sleep 0.5
done

echo "PostgreSQL is up!"

#  Make migrations only if needed
echo "Checking for model changes..."
python manage.py makemigrations --check --dry-run || \
    python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Start Django server on the dynamic port
echo "Starting Django server ..."
exec python manage.py runserver 0.0.0.0:8001
