FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk update && apk add build-base postgresql-dev libffi-dev openssl-dev

COPY requirements.txt ./

CMD [ "pip", "install", "-r", "requirements.txt", "-t", "dist" ]