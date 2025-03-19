FROM python:3.9

RUN apt-get update

RUN pip install --upgrade pip 

WORKDIR /app
COPY app/ /app
RUN mkdir -p /app/outputs/{data,logs}
RUN pip install -r requirements.txt