FROM python:latest

WORKDIR /app

RUN apt-get update -qq && \
    apt-get install -y git python3-pip build-essential

COPY . /app
RUN python3 -m pip install -r requirements.txt
