FROM python:3
ENV PYTHONUNBUFFERED 1

MAINTAINER AvenueCode

RUN mkdir /qaapitest
WORKDIR /qaapitest

#Copy files
COPY requirements.txt /qaapitest/

#Run pip3
RUN pip3 install -r requirements.txt

COPY . /qaapitest
ADD . /qaapitest
