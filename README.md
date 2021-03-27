## How to use

Install hummingbird here: https://github.com/richardycao/hummingbird_python

`cd /basic-bird`

`python3.7 test-pipeline.py` test-pipeline.py is an example for editing and building a pipeline. Run the example to build the docker pipeline.

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-test.yml up` Starts the example data pipeline
