#include <iostream>
#include <vector>
#include <librdkafka/rdkafka.h>
#include <unistd.h>
#include <jansson.h>

static volatile sig_atomic_t run = 1;

/**
 * @brief Signal termination of program
 */
static void stop (int sig) {
    run = 0;
}

/**
 * @returns 1 if all bytes are printable, else 0.
 */
static int is_printable(const char *buf, size_t size) {
    size_t i;

    for (i = 0 ; i < size ; i++)
        if (!isprint((int)buf[i]))
            return 0;

    return 1;
}

//static int shutdown = 0;
static void old_msg_process(rd_kafka_message_t *rkm) {
    // Print the message value/payload.
    if (rkm->payload && is_printable((const char *)rkm->payload, rkm->len)) {
        printf(" Value: %.*s\n", (int)rkm->len, (const char *)rkm->payload);

        json_error_t json_err;
        json_t *json = json_loadb((const char *)rkm->payload, rkm->len, JSON_ALLOW_NUL, &json_err);
        
        if (!json) {
            std::cout << "failed to convert message to json" << std::endl;
        } else {
            std::cout << "Message has successfully been converted to json." << std::endl;
            

            json_decref(json);
        }
    }
    else if (rkm->payload) {
        printf(" Value: (%d bytes)\n", (int)rkm->len);
    }
}

static void process_message(json_t *json) {
    std::cout << "process message" << std::endl;
}

void consume_loop(rd_kafka_t *rk, rd_kafka_topic_partition_list_t *subscriptions) {
    rd_kafka_resp_err_t err;

    if ((err = rd_kafka_subscribe(rk, subscriptions))) {
        fprintf(stderr, "%% Failed to start consuming topics: %s\n", rd_kafka_err2str(err));
        rd_kafka_topic_partition_list_destroy(subscriptions);
        rd_kafka_destroy(rk);
        exit(1);
    }
    rd_kafka_topic_partition_list_destroy(subscriptions);

    // Signal handler for clean shutdown
    signal(SIGINT, stop);

    bool running = true;
    while (running) {
        rd_kafka_message_t *rkm = rd_kafka_consumer_poll(rk, 100);
        if (!rkm)
            continue;
        else if (rkm->err) {
            fprintf(stderr, "%% Consumer error: %s\n", rd_kafka_message_errstr(rkm));
            rd_kafka_message_destroy(rkm);
            continue;
        }
        else if (rkm->len > 0) {
            json_error_t json_err;
            json_t *json = json_loadb((const char *)rkm->payload, rkm->len, JSON_ALLOW_NUL, &json_err);

            if (!json) {
                // Update this error message later.
                fprintf(stderr, "%% Failed to convert rkmessage to json.\n");
            } else {
                process_message(json);
                json_decref(json);
            }
        }

        // old_msg_process(rkm);
        rd_kafka_message_destroy(rkm);
        running = false;
    }

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
    rd_kafka_topic_partition_list_t *subscriptions;
    int topic_count = 1;
    
    char hostname[128];
    char errstr[512];

    conf = rd_kafka_conf_new();

    if (gethostname(hostname, sizeof(hostname))) {
        fprintf(stderr, "%% Failed to lookup hostname\n");
        rd_kafka_conf_destroy(conf);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "client.id", hostname, errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        rd_kafka_conf_destroy(conf);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "bootstrap.servers", "localhost:9092", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        rd_kafka_conf_destroy(conf);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "group.id", "test1", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%% %s\n", errstr);
        rd_kafka_conf_destroy(conf);
        exit(1);
    }

    if (rd_kafka_conf_set(conf, "auto.offset.reset", "earliest", errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
        fprintf(stderr, "%s\n", errstr);
        rd_kafka_conf_destroy(conf);
        exit(1);
    }

    rd_kafka_t *rk;
    if (!(rk = rd_kafka_new(RD_KAFKA_CONSUMER, conf, errstr, sizeof(errstr)))) {
        fprintf(stderr, "%% Failed to create new consumer: %s\n", errstr);
        exit(1);
    }
    conf = NULL; // Configuration object is now owned, and freed, by the rd_kafka_t instance.

    subscriptions = rd_kafka_topic_partition_list_new(topic_count);
    rd_kafka_topic_partition_list_add(subscriptions, "raw", RD_KAFKA_PARTITION_UA);

    consume_loop(rk, subscriptions);

    rd_kafka_destroy(rk);

    return 0;
}

/*
Works with librdkafka and jansson:
/usr/bin/clang++ -O3 -Wall preprocessor.cpp -std=c++11 -lrdkafka -lpthread -lz -lstdc++ -ljansson -o preprocessor

*/

/*
Works with librdkafka:
/usr/bin/clang++ -O3 -Wall preprocessor.cpp -std=c++11 -lrdkafka -lpthread -lz -lstdc++ -o preprocessor
(also work with `g++ ...`)

also works (simpler):
/usr/bin/clang++ -Wall -g -c preprocessor.cpp -std=c++11 -o preprocessor

*/