FROM python:3.7-alpine

RUN mkdir /app
WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY ./app /app

RUN adduser -D user
USER user