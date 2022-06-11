# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.1.13
ENV UWSGI_PIP_VERSION=2.0.20
ENV PSYCOPG2_PIP_VERSION=2.9.3

WORKDIR /app
RUN apt update && apt install gettext -y
RUN pip install "poetry==$POETRY_VERSION" "uwsgi==$UWSGI_PIP_VERSION" "psycopg2==$PSYCOPG2_PIP_VERSION"
ADD . /app
RUN poetry install --no-dev
ENTRYPOINT ["/app/entrypoint.sh"]
