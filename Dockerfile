#
# API Base
#
FROM python:3.9-slim AS backend_base
RUN apt-get update
RUN apt-get install -y curl
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN-PROJECT=false \
    POETRY_HOME=/usr/local/src/poetry
ENV PATH="${POETRY_HOME}/bin:$PATH"

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

#
# API
#
FROM backend_base AS backend
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

COPY . .

ENTRYPOINT /app/entrypoint.sh
