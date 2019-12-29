FROM python:3.7

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY ./pyproject.toml /usr/src/app/pyproject.toml
COPY ./poetry.lock /usr/src/app/poetry.lock

# install requirements
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --quiet

# add app --no-interaction
COPY . /usr/src/app

# run server
CMD flask run --with-threads -h 0.0.0.0
