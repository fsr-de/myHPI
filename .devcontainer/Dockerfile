FROM mcr.microsoft.com/devcontainers/python:3.11

# Add more tools here
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        nano \
        pipx \
        gettext \
    && true

#ENV PATH="${PATH}:~/.local/bin"
#RUN pipx ensurepath
ENV POETRY_VERSION=1.3.2

# README steps
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry self add "poetry-dynamic-versioning[plugin]"

ENV SHELL=/bin/bash