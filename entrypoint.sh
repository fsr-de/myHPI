#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py compilemessages

exec "$@"
