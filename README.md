# Version 2

I'm returning to this project after ~6 months to test an algorithm. I'm running the newer prototype of this project on AWS using gRPC, but realized Kafka might be better for running this algorithm on real-time data, which is why I'm trying to revive basic_bird.

## What is this?

A testing repository for the code-sharing pipeline development framework, hummingbird.

## How to use

Install Docker and docker-compose: https://docs.docker.com/get-docker/

Install hummingbird: https://github.com/richardycao/hummingbird_python

`git clone https://github.com/richardycao/basic_bird.git`

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline. Replace "test-pipeline" with the name of the file that contains your pipeline definition and pipeline.build().

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-<pipeline-id>.yml up` Starts the data pipeline with id of <pipeline-id>. Recall pipeline-id is set in the pipeline definition file.

## Issues

First thing I noticed was that I have to delete the kafka and zookeeper container after each run and rebuild them for the next run. Otherwise kafka runs into an issue that I haven't yet diagnosed.

Another issue, just like before, I can't remember if this supports 1-to-many connections or many-to-1 connections so don't expect those to work. Stick with 1-to-1 connections for now.

## Other Notes

Stick with Module2 and Pipeline2. It will make your life much easier than using the original Module and Pipeline classes. I can't remember all the differences but there are a lot less things that need to be defined during Module development, which makes the developer's life much easier. More things are automated behind the scenes. Look at examples of modules-python vs. modules2-python to see some differences.

params.json is generated when pipeline.build() is called. It contains the parameters you defined in the pipeline.

settings.json must be manually defined. It only supports 1 setting right now, which is use_custom_docker_file. I can't remember what happens if you don't provide a settings file.

There are a bunch of useless files in this repo so it's not easy to navigate or understand. I should clean this up or make a new repo - probably leaning toward the latter, especially since I'm moving it to AWS anyway.

I don't have a tutorial for how to use this. It was a miracle that I remembered how to use it and ran into minimal bugs on my first try. I need to write a tutorial.

## More things to do
Modules could have an onMessage() function instead of run(). This way, users don't have to implement all the loop-related stuff.

# Version 1 (Outdated)

## What is this?

TL;DR A testing repository for a cryptocurrency trading framework.

This framework simplifies the process of developing trading infrastructure from scratch. It enables users to build modular trading pipelines, using publicly available or custom-made modules. From the trader side, modules are dependency-free and easy to include into a pipeline. This minimizes the amount of code a trader needs to write for a specific strategy. From the developer side, each module is easy to implement to perform a specific task. Much of the boilerplate code for the pipeline and module I/O has been abstracted.

Pipeline modules are built using the hummingbird Python library (https://github.com/richardycao/hummingbird_python), which is a framework for building modular data pipelines. Developers can code custom implementations of the hummingbird Module, and share them publicly. Traders can integrate publicly available modules into their own pipelines. Individual modules are run on Docker containers, eliminating any worries about dependencies. Modules (containers) will send messages to each other using the Kafka messaging broker, all automated under the hood, simulating a pipeline.

This repository, basic_bird, has some of my custom hummingbird Modules, under `/modules-python`, which I use for testing.

## How to use

Install Docker and docker-compose: https://docs.docker.com/get-docker/

Install hummingbird: https://github.com/richardycao/hummingbird_python

`git clone https://github.com/richardycao/basic_bird.git`

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline.

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-test1.yml up` Starts the example data pipeline, where "test1" is the pipeline id that is set in test-pipeline.py

## Known or potential issues

Need to check if a module can send data successfully to multiple other modules.
Definitely doesn't work: module receives data from multiple other modules.