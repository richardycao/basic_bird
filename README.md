## What is this?

TL;DR A testing repository for my cryptocurrency trading framework.

The hummingbird Python library (https://github.com/richardycao/hummingbird_python) is a framework for building modular data pipelines to trade cryptocurrency. It allows developers to code their custom implementations of the hummingbird Module, and share them publicly. This enables other developers to integrate publicly available modules into their own pipelines. Individual modules are run on Docker containers, eliminating any worries about dependencies, especially when using modules developed by different parties.

Hummingbird abstracts all I/O from the developer and the user, allowing them to focus purely on module functionality.

This repository, basic_bird, has some of my custom implementations of hummingbird modules, which I use for testing.

## How to use

Install hummingbird here: https://github.com/richardycao/hummingbird_python

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline.

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-test.yml up` Starts the example data pipeline
