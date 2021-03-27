## What is this?

TL;DR A testing repository for a cryptocurrency trading framework.

The hummingbird Python library (https://github.com/richardycao/hummingbird_python) is a framework for building modular data pipelines, using the hummingbird Module, to trade cryptocurrencies. Developers can code custom implementations of the hummingbird Module, and share them publicly. All other developers can integrate publicly available modules into their own pipelines. Individual modules are run on Docker containers, eliminating any worries about dependencies. They send messages to each other using the Kafka messaging broker, simulating a pipeline.

Hummingbird abstracts all pipeline I/O (Kafka and Docker) and other boilerplate from the module developer and the trader.

This repository, basic_bird, has some of my custom hummingbird Modules, under `/modules-python`, which I use for testing.

## How to use

Install Docker and docker-compose: https://docs.docker.com/get-docker/

`pip install pathlib2`

Install hummingbird: https://github.com/richardycao/hummingbird_python

`git clone https://github.com/richardycao/basic_bird.git`

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline.

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-test.yml up` Starts the example data pipeline
