FROM node:18

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# add environment variables
ARG NODE_ENV
ARG VITE_APP_API_URL
ENV NODE_ENV $NODE_ENV
ENV VITE_APP_API_URL $VITE_APP_API_URL

# install dependencies
COPY package.json /usr/src/app/package.json
COPY yarn.lock /usr/src/app/yarn.lock
RUN yarn install --silent

# copy source
COPY . /usr/src/app/