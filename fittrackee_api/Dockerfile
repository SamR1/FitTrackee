FROM python:3.6.3

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY ./requirements.txt /usr/src/app/fittrackee_api/requirements.txt

# install requirements
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# add app
COPY . /usr/src/app

# run server
CMD flask run --with-threads -h 0.0.0.0
