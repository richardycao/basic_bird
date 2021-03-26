## How to use

Install hummingbird here: https://github.com/richardycao/hummingbird_python

Clone this repo

`cd /basic-bird`

`python3.7 test-pipeline.py` Example for editing and building a pipeline

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

The new pipeline doesn't support this last step yet, since linking isn't done.

`docker-compose -f docker-compose-test.yml up` Starts the data pipeline
