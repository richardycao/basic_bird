## How to use

`cd /basic-bird`

`docker-compose -f docker-compose-kafka.yml build` Builds kafka

`docker-compose -f docker-compose-pipeline.yml build` Builds the data pipeline

`docker-compose -f docker-compose-kafka.yml up` Starts kafka

Wait ~1 minute for kafka to start up.

`docker-compose -f docker-compose-pipeline.yml up` Starts the data pipeline

## Logs

https://www.dropbox.com/scl/fi/wfk0j21hhtwpre6znbmdw/Crypto.paper?dl=0&rlkey=oyly68nqqgshph4ct0y6u3k02
