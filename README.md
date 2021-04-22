## What is this?

TL;DR A testing repository for a cryptocurrency trading framework.

This framework simplifies the process of developing trading infrastructure from scratch. It enables users to build modular trading pipelines, using publicly available or custom-made modules. From the trader side, modules are dependency-free and easy to include into a pipeline. This minimizes the amount of code a trader needs to write for a specific strategy. From the developer side, each module is easy to implement to perform a specific task. Much of the boilerplate code for the pipeline and module I/O has been abstracted.

Pipeline modules are built using the hummingbird Python library (https://github.com/richardycao/hummingbird_python), which is a framework for building modular data pipelines. Developers can code custom implementations of the hummingbird Module, and share them publicly. Traders can integrate publicly available modules into their own pipelines. Individual modules are run on Docker containers, eliminating any worries about dependencies. Modules (containers) will send messages to each other using the Kafka messaging broker, all automated under the hood, simulating a pipeline.

This repository, basic_bird, has some of my custom hummingbird Modules, under `/modules-python`, which I use for testing.

## How to use (outdated since Module v2)

Install Docker and docker-compose: https://docs.docker.com/get-docker/

Install hummingbird: https://github.com/richardycao/hummingbird_python

`git clone https://github.com/richardycao/basic_bird.git`

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline.

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-test1.yml up` Starts the example data pipeline, where "test1" is the pipeline id that is set in test-pipeline.py
