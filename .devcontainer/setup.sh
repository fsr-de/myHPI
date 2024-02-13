#!/bin/bash
python -m venv env
source env/bin/activate
poetry install
if python tools/install_bootstrap.py --is-installed; then
    echo "Bootstrap is already installed."
else
    python tools/install_bootstrap.py
fi

if [ ! -f .env ]; then
    cp .env.example .env
fi

python manage.py migrate
python manage.py compilemessages
