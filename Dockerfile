FROM python:3.10

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# copy source files
COPY . /usr/src/app

# install requirements
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install poetry
RUN . $VIRTUAL_ENV/bin/activate && poetry install --no-interaction --quiet

# run fittrackee server
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
COPY ./docker/set-admin.sh /usr/bin/set-admin
RUN chmod +x /usr/bin/set-admin && chmod +x /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]