FROM node:24-alpine AS node-builder

RUN mkdir -p /usr/src/app/fittrackee_client /usr/src/app/fittrackee
WORKDIR /usr/src/app/fittrackee_client

ENV PATH=/usr/src/app/fittrackee_client/node_modules/.bin:$PATH
COPY fittrackee_client/package.json /usr/src/app/fittrackee_client/package.json
COPY fittrackee_client/package-lock.json /usr/src/app/fittrackee_client/package-lock.json
RUN apk add --no-cache git
RUN npm ci --ignore-scripts --silent --network-timeout 300000 && \
	npm cache clean --force

COPY fittrackee_client/. /usr/src/app/fittrackee_client
RUN npm run build

FROM python:3.13-alpine AS python-builder

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    VIRTUAL_ENV=/opt/venv

COPY pyproject.toml poetry.lock README.md /usr/src/app/
COPY fittrackee/. /usr/src/app/fittrackee/
RUN rm -rf /usr/src/app/fittrackee/tests

RUN apk add --no-cache g++ gdal-dev && \
    rm -rf /var/cache/apk/* && \
    python3 -m venv "$VIRTUAL_ENV" && \
    pip install --upgrade pip wheel && \
    pip install poetry==2.3.3 && \
    . "$VIRTUAL_ENV/bin/activate" && \
    poetry install --only main --no-interaction --quiet

FROM python:3.13-alpine AS runtime

RUN apk add --no-cache tini libmagic && \
    addgroup -g 1000 -S fittrackee && \
    adduser -H -D -u 1000 -S fittrackee -G fittrackee

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH"

COPY --chown=root --chmod=755 --from=python-builder /opt/venv "$VIRTUAL_ENV"
COPY --chown=root --chmod=755 --from=python-builder /usr/src/app/fittrackee /usr/src/app/fittrackee
COPY --chown=root --chmod=755 --from=node-builder /usr/src/app/fittrackee/dist /usr/src/app/fittrackee/dist
COPY --chown=root --chmod=755 docker-entrypoint.sh /usr/src/app/

USER fittrackee

ENTRYPOINT ["/sbin/tini", "--"]