#
# API Base
#
FROM python:3.9-slim AS backend_base
RUN apt-get update
RUN apt-get install -y curl
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN-PROJECT=true \
    POETRY_HOME=/usr/local/src/poetry
ENV PATH="${POETRY_HOME}/bin:$PATH"

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

#
# API
#
FROM backend_base AS backend
USER carto
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .

ENTRYPOINT entrypoint.sh
