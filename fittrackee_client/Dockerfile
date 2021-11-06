FROM node:16

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# add environment variables
ARG NODE_ENV
ARG VUE_APP_API_URL
ENV NODE_ENV $NODE_ENV
ENV VUE_APP_API_URL $VUE_APP_API_URL

# install dependencies
COPY package.json /usr/src/app/package.json
RUN yarn install --silent
RUN yarn global add @vue/cli

# copy source
COPY . /usr/src/app/