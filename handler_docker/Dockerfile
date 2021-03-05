# Get the base Ubuntu image from Docker Hub
FROM ubuntu:latest

# Update apps on the base image
RUN apt-get -y update && apt-get install -y

# Install the Clang compiler
RUN apt-get -y install clang

# Install Apache Kafka for C++
RUN apt-get -y install librdkafka-dev

# Install Jansson for C++
RUN apt-get install -y libjansson-dev

# Copy the current folder which contains C++ source code to the Docker image under /usr/src
COPY . /usr/src/preprocessor

# Specify the working directory
WORKDIR /usr/src/preprocessor

# Use Clang to compile the Test.cpp source file
RUN clang++ -O3 -Wall preprocessor.cpp -std=c++11 -lrdkafka -lpthread -lz -lstdc++ -o preprocessor

# Run the output program from the previous step
CMD ["./preprocessor"]