FROM python:3.11

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.4.2

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chgrp -R 0 $POETRY_HOME && \
    chmod -R g+rwX $POETRY_HOME

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN poetry config virtualenvs.create false && \
    poetry install --without test --no-root

COPY . /app

RUN poetry build && \
    poetry install --without test --no-interaction --no-ansi