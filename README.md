`cd /basic-bird`

`docker-compose build` build the docker containers

`docker-compose up` to start the docker containers

`python3.7 local/predictor_v2.py` Predictor starts waiting on the preprocessor

`/usr/bin/clang++ -O3 -Wall handler_docker/preprocessor_v3.cpp -std=c++11 -lrdkafka++ -lpthread -lz -lstdc++ -ljsoncpp -o handler_docker/preprocessor_v3` Compiles the preprocessor

`./handler_docker/preprocessor_v3 -t test -u processed2 -p 0` Preprocessor start waiting on messages from the producer.

`python3.7 local/producer_v2.py` Producer begins producing messages for the preprocessor