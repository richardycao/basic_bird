FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.7 python3-pip python3-dev
RUN apt-get install -y git
RUN pip3 install --upgrade pip

WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt
RUN pip3 uninstall hummingbird
RUN pip3 install --upgrade git+https://github.com/richardycao/hummingbird_python.git#egg=hummingbird

CMD python3 cbp-historic-rates.py --topics-in pipeline-v1-0 --topics-out pipeline-v1-1 --start 2021-02-08T00:00:00.000Z --stop 2021-04-07T00:00:00.000Z
