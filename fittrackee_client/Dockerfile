FROM node:11.6.0

MAINTAINER SamR1@users.noreply.github.com

# set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# add environment variables
ARG REACT_APP_API_URL
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
ENV REACT_APP_API_URL $REACT_APP_API_URL

# install and cache app dependencies
COPY package.json /usr/src/app/package.json
RUN yarn install --silent
RUN yarn global add react-scripts

# add app
COPY . /usr/src/app/

# start app
CMD yarn start
