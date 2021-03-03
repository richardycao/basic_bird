`cd /basic-bird`

`docker-compose build` build the docker containers

`docker-compose up` to start the docker containers

`cd /local`

`python3.7 predictor.py` Predictor start waiting on the consumer

`python3.7 consumer.py` Consumer starts waiting on the producer

`python3.7 producer.py` Producer begins producing messages for the consumer

C++ preprocessor in development