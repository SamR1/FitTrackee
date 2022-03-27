FROM python:3.9

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# copy source files
COPY . /usr/src/app

# install requirements
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --quiet

# create uploads folder
CMD mkdir /usr/src/app/uploads

# run fittrackee server
CMD flask run --with-threads -h 0.0.0.0