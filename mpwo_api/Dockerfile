FROM python:3.6.3

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY ./requirements.txt /usr/src/app/mpwo_api/requirements.txt

# install requirements
RUN pip install -r mpwo_api/requirements.txt

# add app
COPY . /usr/src/app
COPY ../migrations /usr/src/app

# run server
CMD flask run --with-threads -h 0.0.0.0
