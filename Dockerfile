# base
FROM python:3.11-alpine3.17 AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    libffi-dev \
    musl-dev

# node-builder
FROM node:18-alpine3.17 AS node-builder

WORKDIR /app

COPY vocexcel-ui/ .

RUN npm ci
RUN npm run build

# python-builder
FROM base AS python-builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install poetry

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --with web | pip install -r /dev/stdin

COPY . .
COPY --from=node-builder /app/dist /app/vocexcel/static
RUN poetry build && pip install dist/*.whl

# final
FROM base as final

COPY --from=node-builder /app/dist /vocexcel-ui
COPY --from=python-builder /opt/venv /opt/venv

ENV VIRTUALENV=/opt/venv \
    PATH=/opt/venv/bin:${PATH} \
    VOCEXCEL_WEB_STATIC_DIR=/opt/venv/lib/python3.11/site-packages/vocexcel/static

RUN apk --no-cache add bash

USER 1000

CMD [ "uvicorn", "vocexcel.web.app:create_app", "--host=0.0.0.0", "--port=8000", "--proxy-headers" ]
