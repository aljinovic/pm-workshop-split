# Base image from https://hub.docker.com/_/python/ on top of which we're building our image
FROM python:3.7-alpine

# The directory inside docker container which will be used
WORKDIR /app

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile* /app/

# Dependencies required for packages installed using Pipenv
RUN apk add build-base libxslt-dev libxml2-dev postgresql-dev

# Install Pipenv and then install requirements
RUN pip install pipenv && pipenv install --system

# Copy application code inside working directory
COPY . /app

# Command that runs the application
CMD ["python", "app.py", "--help"]

# Port exposed to other containers (not used yet)
EXPOSE 80
