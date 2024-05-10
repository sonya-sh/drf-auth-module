#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$REDIS_ENABLED" = "true" ]; then
    echo "Waiting for Redis..."
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
      sleep 0.1
    done
    echo "Redis started"
fi

# python3 manage.py flush --no-input
# python3 online_school/manage.py migrate

exec "$@"