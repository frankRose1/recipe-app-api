FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev
# temp requiremnts needed for installing some of the pip packages
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
# delete the temp requirements
RUN apk del .tmp-build-deps

COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
# give user ownership of directories in /vol/
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user