# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./docker-entrypoint.sh /code/
RUN sed -i 's/\r$//g' /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh

# copy project
COPY ./backend/ /code/

# set work directory
WORKDIR /code/backend

# run entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]