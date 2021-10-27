FROM node:10.19.0-alpine3.9

WORKDIR /usr/src/app

COPY ./digikofy-front /usr/src/app

RUN npm install

ENV PORT=$PORT

EXPOSE $PORT

CMD ["npm", "build"]
