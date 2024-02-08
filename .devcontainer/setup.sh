#!/bin/bash
poetry install
python tools/install_bootstrap.py
cp .env.example .env
python manage.py migrate
python manage.py compilemessages