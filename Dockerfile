FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt update \
  && apt install -y build-essential less libpq-dev postgresql-client \
  procps wget \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
COPY requirements-development.txt /app/
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -Ur /app/requirements.txt \
  && pip install --no-cache-dir -Ur /app/requirements-development.txt;

COPY . /app

CMD "/app/bin/web.sh"
