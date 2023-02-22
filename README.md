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
