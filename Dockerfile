FROM python:3.11-slim as builder
RUN apt-get update && apt-get install -y gcc git
ADD requirements.txt  ./
RUN pip3 install -r requirements.txt

RUN mkdir -p /app
WORKDIR /app
ADD . /app
RUN ape plugins install -y .

ENTRYPOINT ["./entrypoint.sh"]
