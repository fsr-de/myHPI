#!/bin/bash

python manage.py migrate
python manage.py compilestatic
python manage.py collectstatic --no-input
python manage.py compilemessages
python manage.py publish_release_post

exec "$@"
