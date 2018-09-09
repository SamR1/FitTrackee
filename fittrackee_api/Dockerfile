FROM python:3.7

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY ./Pipfile /usr/src/app/Pipfile
COPY ./Pipfile.lock /usr/src/app/Pipfile.lock

# install requirements
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --dev

# add app
COPY . /usr/src/app

# run server
CMD flask run --with-threads -h 0.0.0.0
