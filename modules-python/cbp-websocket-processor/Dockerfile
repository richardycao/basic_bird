FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.7 python3-pip python3-dev
RUN apt-get install -y git
RUN pip3 install --upgrade pip

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 uninstall hummingbird
RUN pip3 install git+https://github.com/richardycao/hummingbird_python.git#egg=hummingbird

COPY *.py .
CMD python3 cbp-websocket-processor.py --topics-in test1-1 --topics-out test1-2
