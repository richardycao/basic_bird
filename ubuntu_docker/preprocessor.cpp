#include <iostream>
#include <librdkafka>

static int shutdown = 0;
static void msg_process(rd_kafka_message_t message) {
    std::cout << "process" << std::endl;
}

void basic_consume_loop(rd_kafka_t *rk, rd_kafka_topic_partition_list_t *topics) {
    rd_kafka_resp_err_t err;

    if ((err = rd_kafka_subscribe(rk, topics))) {
        fprintf(stderr, "%% Failed to start consuming topics: %s\n", rd_kafka_err2str(err));
        exit(1);
    }

    while (running) {
        rd_kafka_message_t *rkmessage = rd_kafka_consumer_poll(rk, 500);
        if (rkmessage) {
        msg_process(rkmessage);
        rd_kafka_message_destroy(rkmessage);
        }
    }

    err = rd_kafka_consumer_close(rk);
    if (err)
        fprintf(stderr, "%% Failed to close consumer: %s\n", rd_kafka_err2str(err));
    else
        fprintf(stderr, "%% Consumer closed\n");
}

int main(int argc, char const *argv[])
{
    for (int i=0; i<1000; i++) {
        std::cout << "Hello Docker container!" << std::endl;
    }
    return 0;
}