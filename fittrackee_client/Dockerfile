FROM node:13.13.0

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# add environment variables
ARG REACT_APP_API_URL
ARG NODE_ENV
ARG REACT_APP_ALLOW_REGISTRATION
ARG CI
ENV NODE_ENV $NODE_ENV
ENV REACT_APP_API_URL $REACT_APP_API_URL
ENV REACT_APP_ALLOW_REGISTRATION $REACT_APP_ALLOW_REGISTRATION
ENV CI $CI

# install and cache app dependencies
COPY package.json /usr/src/app/package.json
RUN yarn install --silent
RUN yarn global add react-scripts

# add app
COPY . /usr/src/app/

# start app
CMD yarn start
