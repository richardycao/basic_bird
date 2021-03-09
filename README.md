`cd /basic-bird`

`docker-compose build` build the docker containers

`docker-compose up` to start the docker containers

`python3.7 local/predictor.py` Predictor start waiting on the preprocessor

`/usr/bin/clang++ -O3 -Wall handler_docker/preprocessor_v3.cpp -std=c++11 -lrdkafka++ -lpthread -lz -lstdc++ -ljsoncpp -o handler_docker/preprocessor_v3` to compile the preprocessor

`./handler_docker/preprocessor_v3 -t raw2 -u processed2 -p 0` to start the preprocessor

`python3.7 local/producer.py` Producer begins producing messages for the preprocessor

C++ preprocessor in development