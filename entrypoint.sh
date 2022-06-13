#!/bin/sh

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py compilemessages

exec "$@"
