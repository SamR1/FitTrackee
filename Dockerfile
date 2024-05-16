#FROM python:3.10-slim
FROM python:3.10-alpine

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# copy source files
COPY . /usr/src/app

# install gcc
#RUN apt update && apt install gcc python3-dev -y
RUN apk add --no-cache linux-headers gcc musl-dev libffi-dev py-pip bash

# install requirements
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir poetry
RUN . $VIRTUAL_ENV/bin/activate && poetry install --no-interaction

# run fittrackee server
CMD flask run --with-threads -h 0.0.0.0
