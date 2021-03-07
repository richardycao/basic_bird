#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <csignal>
#include <cstring>

#ifdef _WIN32
#include "../win32/wingetopt.h"
#elif _AIX
#include <unistd.h>
#else
#include <getopt.h>
#endif

#include <librdkafka/rdkafkacpp.h>

static volatile sig_atomic_t run = 1;
static bool exit_eof = false;

static void sigterm (int sig) {
  run = 0;
}

class ExampleDeliveryReportCb : public RdKafka::DeliveryReportCb {
 public:
  void dr_cb (RdKafka::Message &message) {
    std::string status_name;
    switch (message.status())
      {
      case RdKafka::Message::MSG_STATUS_NOT_PERSISTED:
        status_name = "NotPersisted";
        break;
      case RdKafka::Message::MSG_STATUS_POSSIBLY_PERSISTED:
        status_name = "PossiblyPersisted";
        break;
      case RdKafka::Message::MSG_STATUS_PERSISTED:
        status_name = "Persisted";
        break;
      default:
        status_name = "Unknown?";
        break;
      }
    std::cout << "Message delivery for (" << message.len() << " bytes): " <<
      status_name << ": " << message.errstr() << std::endl;
    if (message.key())
      std::cout << "Key: " << *(message.key()) << ";" << std::endl;
  }
};

class ExampleEventCb : public RdKafka::EventCb {
 public:
  void event_cb (RdKafka::Event &event) {
    switch (event.type())
    {
      case RdKafka::Event::EVENT_ERROR:
        if (event.fatal()) {
          std::cerr << "FATAL ";
          run = 0;
        }
        std::cerr << "ERROR (" << RdKafka::err2str(event.err()) << "): " <<
            event.str() << std::endl;
        break;

      case RdKafka::Event::EVENT_STATS:
        std::cerr << "\"STATS\": " << event.str() << std::endl;
        break;

      case RdKafka::Event::EVENT_LOG:
        fprintf(stderr, "LOG-%i-%s: %s\n",
                event.severity(), event.fac().c_str(), event.str().c_str());
        break;

      default:
        std::cerr << "EVENT " << event.type() <<
            " (" << RdKafka::err2str(event.err()) << "): " <<
            event.str() << std::endl;
        break;
    }
  }
};

/* Use of this partitioner is pretty pointless since no key is provided
 * in the produce() call. */
class MyHashPartitionerCb : public RdKafka::PartitionerCb {
 public:
  int32_t partitioner_cb (const RdKafka::Topic *topic, const std::string *key,
                          int32_t partition_cnt, void *msg_opaque) {
    return djb_hash(key->c_str(), key->size()) % partition_cnt;
  }
 private:

  static inline unsigned int djb_hash (const char *str, size_t len) {
    unsigned int hash = 5381;
    for (size_t i = 0 ; i < len ; i++)
      hash = ((hash << 5) + hash) + str[i];
    return hash;
  }
};

void msg_consume(RdKafka::Message* message, void* opaque) {
  const RdKafka::Headers *headers;

  switch (message->err()) {
    case RdKafka::ERR__TIMED_OUT:
      break;

    case RdKafka::ERR_NO_ERROR:
      /* Real message */
      std::cout << "Read msg at offset " << message->offset() << std::endl;
      if (message->key()) {
        std::cout << "Key: " << *message->key() << std::endl;
      }
      headers = message->headers();
      if (headers) {
        std::vector<RdKafka::Headers::Header> hdrs = headers->get_all();
        for (size_t i = 0 ; i < hdrs.size() ; i++) {
          const RdKafka::Headers::Header hdr = hdrs[i];

          if (hdr.value() != NULL)
            printf(" Header: %s = \"%.*s\"\n",
                   hdr.key().c_str(),
                   (int)hdr.value_size(), (const char *)hdr.value());
          else
            printf(" Header:  %s = NULL\n", hdr.key().c_str());
        }
      }
      printf("%.*s\n",
        static_cast<int>(message->len()),
        static_cast<const char *>(message->payload()));
      break;

    case RdKafka::ERR__PARTITION_EOF:
      /* Last message */
      if (exit_eof) {
        run = 0;
      }
      break;

    case RdKafka::ERR__UNKNOWN_TOPIC:
    case RdKafka::ERR__UNKNOWN_PARTITION:
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
      run = 0;
      break;

    default:
      /* Errors */
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
      run = 0;
  }
}

int main(int argc, char **argv) {
  std::string brokers = "localhost";
  std::string errstr;
  int64_t start_offset = RdKafka::Topic::OFFSET_BEGINNING;
  int opt;
  MyHashPartitionerCb hash_partitioner;

  // Consumer objects
  std::string topic_str_in;
  int32_t partition_in = RdKafka::Topic::PARTITION_UA;
  RdKafka::Conf *conf_in  = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
  RdKafka::Conf *tconf_in = RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC);
  
  // Producer objects
  std::string topic_str_out;
  int32_t partition_out = RdKafka::Topic::PARTITION_UA;
  RdKafka::Conf *conf_out  = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);
  RdKafka::Conf *tconf_out = RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC);

  while ((opt = getopt(argc, argv, "Lp:q:b:o:t:u:")) != -1) {
    switch (opt) {
      case 't':
        topic_str_in = optarg;
        break;
      case 'u':
        topic_str_out = optarg;
        break;
      case 'p':
        if (!strcmp(optarg, "random"))
          /* default */;
        else if (!strcmp(optarg, "hash")) {
          if (tconf_in->set("partitioner_cb", &hash_partitioner, errstr) != RdKafka::Conf::CONF_OK) {
            std::cerr << errstr << std::endl;
            exit(1);
          }
        } else
          partition_in = std::atoi(optarg);
        break;
      case 'q':
        if (!strcmp(optarg, "random"))
          /* default */;
        else if (!strcmp(optarg, "hash")) {
          if (tconf_out->set("partitioner_cb", &hash_partitioner, errstr) != RdKafka::Conf::CONF_OK) {
            std::cerr << errstr << std::endl;
            exit(1);
          }
        } else
          partition_out = std::atoi(optarg);
        break;
      case 'b':
        brokers = optarg;
        break;
      case 'o':
        if (!strcmp(optarg, "end"))
          start_offset = RdKafka::Topic::OFFSET_END;
        else if (!strcmp(optarg, "beginning"))
          start_offset = RdKafka::Topic::OFFSET_BEGINNING;
        else if (!strcmp(optarg, "stored"))
          start_offset = RdKafka::Topic::OFFSET_STORED;
        else
          start_offset = strtoll(optarg, NULL, 10);
        break;
      default:
        goto usage;
    }
  }

  if ((topic_str_in.empty() || topic_str_out.empty()) || optind != argc) {
    if (topic_str_in.empty() || topic_str_out.empty())
      std::cout << "middle" << std::endl;
    else
      std::cout << "last" << std::endl;
    usage:
      std::string features;
      conf_in->get("builtin.features", features);
      conf_out->get("builtin.features", features);
    exit(1);
  }

  conf_in->set("metadata.broker.list", brokers, errstr);
  conf_out->set("metadata.broker.list", brokers, errstr);

  signal(SIGINT, sigterm);
  signal(SIGTERM, sigterm);

  if(topic_str_in.empty() || topic_str_out.empty())
    goto usage;

  /* ============================== Consumer setup ============================== */
  conf_in->set("enable.partition.eof", "true", errstr);

  // Create consumer using configuration
  RdKafka::Consumer *consumer = RdKafka::Consumer::create(conf_in, errstr);
  if (!consumer) {
    std::cerr << "Failed to create consumer: " << errstr << std::endl;
    exit(1);
  }
  std::cout << "% Created consumer " << consumer->name() << std::endl;

  // Create consumer topic handle.
  RdKafka::Topic *topic_in = RdKafka::Topic::create(consumer, topic_str_in, tconf_in, errstr);
  if (!topic_in) {
    std::cerr << "Failed to create topic: " << errstr << std::endl;
    exit(1);
  }

  // Start consumer for topic+partition at start offset
  RdKafka::ErrorCode resp = consumer->start(topic_in, partition_in, start_offset);
  if (resp != RdKafka::ERR_NO_ERROR) {
    std::cerr << "Failed to start consumer: " << RdKafka::err2str(resp) << std::endl;
    exit(1);
  }

  /* ============================== Producer setup ============================== */
  ExampleDeliveryReportCb ex_dr_cb;

  // Set delivery report callback
  conf_out->set("dr_cb", &ex_dr_cb, errstr);
  conf_out->set("default_topic_conf", tconf_out, errstr);

  // Create producer using accumulated global configuration.
  RdKafka::Producer *producer = RdKafka::Producer::create(conf_out, errstr);
  if (!producer) {
    std::cerr << "Failed to create producer: " << errstr << std::endl;
    exit(1);
  }
  std::cout << "% Created producer " << producer->name() << std::endl;

  /* ============================== Run ============================== */

  // Consume messages
  while (run) {
    RdKafka::Message *msg = consumer->consume(topic_in, partition_in, 1000);
    msg_consume(msg, NULL);
    delete msg;
    consumer->poll(0);
  }

  // Stop consumer
  consumer->stop(topic_in, partition_in);
  consumer->poll(1000);

  std::cout << "Cleaning up memory..." << std::endl;

  delete topic_in;
  delete consumer;
  delete producer;

  delete conf_in;
  delete tconf_in;
  delete conf_out;
  delete tconf_out;
  RdKafka::wait_destroyed(5000);

  return 0;
}

/*
Works with librdkafka and jansson and jansson_parser:
/usr/bin/clang++ -O3 -Wall preprocessor_v3.cpp -std=c++11 -lrdkafka++ -lpthread -lz -lstdc++ -o preprocessor_v3

Command:
./preprocessor_v3 -t raw -u processed -p 0
*/