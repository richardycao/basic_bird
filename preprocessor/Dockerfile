FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.7 python3-pip python3-dev
RUN pip3 install --upgrade pip

WORKDIR /usr/src/preprocessor
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY preprocessor.py .
CMD python3 preprocessor.py