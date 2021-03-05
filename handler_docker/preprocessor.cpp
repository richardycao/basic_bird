#include <iostream>
#include <vector>
#include <librdkafka/rdkafka.h>
#include <unistd.h>

//static int shutdown = 0;
static void msg_process(rd_kafka_message_t *message) {
    std::cout << message << std::endl;
}

void consume_loop(rd_kafka_t *rk, rd_kafka_topic_partition_list_t *topics) {
    rd_kafka_resp_err_t err;
    //std::cout << "start consume loop" << std::endl;

    if ((err = rd_kafka_subscribe(rk, topics))) {
        fprintf(stderr, "%% Failed to start consuming topics: %s\n", rd_kafka_err2str(err));
        exit(1);
    }

    //std::cout << "before if(rkmessage)" << std::endl;

    //while (running) {
        rd_kafka_message_t *rkmessage = rd_kafka_consumer_poll(rk, 500);
        if (rkmessage) {
            //std::cout << "rkmessage exists" << std::endl;
            msg_process(rkmessage);
            rd_kafka_message_destroy(rkmessage);
            //std::cout << "rkmessage destroyed" << std::endl;
        }
    //}

    err = rd_kafka_consumer_close(rk);
    if (err)
        fprintf(stderr, "%% Failed to close consumer: %s\n", rd_kafka_err2str(err));
    else
        fprintf(stderr, "%% Consumer closed\n");
}

int main(int argc, char const *argv[])
{
    for (int i=0; i<1; i++) {
        std::cout << "Hello Docker container!" << std::endl;
    }

    rd_kafka_conf_t *conf;
    // rd_kafka_topic_t *rkt;
    // rd_kafka_topic_conf_t *topic_conf;

    rd_kafka_topic_partition_list_t *topics_list;
    
    char hostname[128];
    char errstr[512];

    conf = rd_kafka_conf_new();

    if (gethostname(hostname, sizeof(hostname))) {
        fprintf(stderr, "%% Failed to lookup hostname\n");
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "client.id", hostname, errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "group.id", "test1", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "bootstrap.servers", "localhost:9092", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        exit(1);
    }

    rd_kafka_t *rk;
    if (!(rk = rd_kafka_new(RD_KAFKA_CONSUMER, conf, errstr, sizeof(errstr)))) {
        fprintf(stderr, "%% Failed to create new consumer: %s\n", errstr);
        exit(1);
    }

    // topic_conf = rd_kafka_topic_conf_new();

    // if (rd_kafka_topic_conf_set(topic_conf, "topic", "raw", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
    //     fprintf(stderr, "%% %s\n", errstr);
    //     exit(1);
    // }

    topics_list = rd_kafka_topic_partition_list_new(1);
    rd_kafka_topic_partition_list_add(topics_list, "raw", 0);

    consume_loop(rk, topics_list);

    return 0;
}

/*
This one works:
/usr/bin/clang++ -O3 -Wall preprocessor.cpp -std=c++11 -lrdkafka -lpthread -lz -lstdc++ -o preprocessor
(also work with `g++ ...`)

also works (simpler):
/usr/bin/clang++ -Wall -g -c preprocessor.cpp -std=c++11 -o preprocessor

*/

/*
Some initial attempts:

/usr/bin/clang++ -g /usr/local/Cellar/librdkafka/1.6.1/include/librdkafka/rdkafka.h /Users/richacao/basic_bird/ubuntu_docker/preprocessor.cpp -o /Users/richacao/basic_bird/ubuntu_docker/preprocessor

/usr/bin/clang++ -c /Users/richacao/basic_bird/ubuntu_docker/preprocessor.cpp -o /Users/richacao/basic_bird/ubuntu_docker/preprocessor.o

/usr/bin/clang++ -c /usr/local/Cellar/librdkafka/1.6.1/include/librdkafka/rdkafka.h -o /Users/richacao/basic_bird/ubuntu_docker/rdkafka.o

/usr/bin/clang++ /Users/richacao/basic_bird/ubuntu_docker/preprocessor.o /Users/richacao/basic_bird/ubuntu_docker/rdkafka.o -o executable

g++ /Users/richacao/basic_bird/ubuntu_docker/preprocessor.cpp
*/