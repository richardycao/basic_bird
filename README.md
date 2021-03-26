## How to use

These instructions are outdated for now.

`cd /basic-bird`

`python3.7 test-pipeline.py` Edit and build the pipeline here

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

The new pipeline doesn't support this last step yet, since linking isn't done.

`docker-compose -f docker-compose-test.yml up` Starts the data pipeline
