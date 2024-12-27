FROM python:3.13-alpine AS BUILDER

# install dependencies
RUN apk add --no-cache linux-headers gcc musl-dev libffi-dev \
    --virtual=build-dependencies
RUN apk add --no-cache py-pip bash curl

# copy source files
RUN LATEST=$(curl -s \
    "https://api.github.com/repos/SamR1/FitTrackee/releases/latest" | \
    grep -i zipball_url | grep -Eo "https://.*[0-9]{1}") && \
    wget "${LATEST}" -O /usr/src/latest.zip
RUN cd /usr/src/ && unzip latest.zip -d /usr/src/app
RUN sync
RUN mv /usr/src/app/*FitTrackee*/* /usr/src/app/
RUN rm -r /usr/src/app/*FitTrackee*/
RUN rm -r /usr/src/latest.zip

# install requirements
WORKDIR /usr/src/app
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir poetry
RUN . $VIRTUAL_ENV/bin/activate && poetry install --no-interaction


FROM python:3.13-alpine

RUN apk add bash

# create user fittrackee
RUN addgroup -g 1000 -S fittrackee
RUN adduser -u 1000 -S -D -G fittrackee -H -h /usr/src/app -s /bin/bash fittrackee

COPY --from=BUILDER /opt/venv/ /opt/venv
COPY --from=BUILDER /usr/src/app /usr/src/app

WORKDIR /usr/src/app
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# change owner
RUN chown -R fittrackee:fittrackee /usr/src/app

# run fittrackee server
USER fittrackee
CMD flask run --with-threads -h 0.0.0.0
