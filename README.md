## How to use

These instructions are outdated for now.

`cd /basic-bird`

`docker-compose -f docker-compose-kafka.yml build` Builds kafka

`docker-compose -f docker-compose-pipeline.yml build` Builds the data pipeline

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-pipeline.yml up` Starts the data pipeline
