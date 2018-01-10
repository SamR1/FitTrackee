FROM python:3.6.3

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
ADD ./requirements.txt /usr/src/app/mpwo_api/requirements.txt

# install requirements
RUN pip install -r mpwo_api/requirements.txt

# add app
ADD . /usr/src/app

# run server
CMD flask run --with-threads -h 0.0.0.0
