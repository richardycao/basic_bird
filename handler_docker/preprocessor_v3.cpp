#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <csignal>
#include <cstring>
#include <map>
#include <vector>
#include <algorithm>

#ifdef _WIN32
#include "../win32/wingetopt.h"
#elif _AIX
#include <unistd.h>
#else
#include <getopt.h>
#endif

#include <librdkafka/rdkafkacpp.h>
#include <json/json.h>

static volatile sig_atomic_t run = 1;
static bool exit_eof = false;

static void sigterm (int sig) {
  run = 0;
}

/* Use of this partitioner is pretty pointless since no key is provided
 * in the produce() call. */
class HashPartitionerCb : public RdKafka::PartitionerCb {
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

std::map<float, float> bids;
std::map<float, float> asks;

void msg_consume(RdKafka::Message* message, void* opaque) {
  Json::CharReaderBuilder builder;
  Json::CharReader *reader = builder.newCharReader();

  Json::Value root;
  std::string msg_str;
  std::string errors;

  bool parse_success;
  switch (message->err()) {
    case RdKafka::ERR__TIMED_OUT:
      break;
    case RdKafka::ERR_NO_ERROR:
    {
      msg_str = static_cast<const char *>(message->payload());
      parse_success = reader->parse(msg_str.c_str(), msg_str.c_str() + msg_str.size(), &root, &errors);
      if (!parse_success) {
          std::cout << "Failed to parse message" << std::endl;
          break;
      }

      std::string type = root["type"].asString();
      if (type.compare("snapshot") == 0) {
        // build order book
        auto bid_orders = root["bids"];
        auto ask_orders = root["asks"];

        // worry about parallelizing later
        // std::transform(asks.begin(), asks.end(), asks.begin(), 
        //   [](Json::Value pair) -> Json::Value { return Json::Value({pair[0], pair[1]}); });

        // can't iterate backwards over a Json array for some reason. It breaks at runtime and is un-interruptable.
        std::string::size_type sz;
        for (Json::Value::ArrayIndex i = 0; i < bid_orders.size(); i++) {
          bids.insert({std::stof(bid_orders[i][0].asString(), &sz), std::stof(bid_orders[i][1].asString(), &sz)});

          // std::cout << std::stof(bid_orders[i][0].asString(), &sz) << " | " << std::stof(bid_orders[i][1].asString(), &sz) << std::endl;
          //std::cout << bid_orders[i] << std::endl;
        }
        for (Json::Value::ArrayIndex i = 0; i < ask_orders.size(); i++) {
          asks.insert({std::stof(ask_orders[i][0].asString(), &sz), std::stof(ask_orders[i][1].asString(), &sz)});

          // std::cout << std::stof(ask_orders[i][0].asString(), &sz) << " | " << std::stof(ask_orders[i][1].asString(), &sz) << std::endl;
          //std::cout << ask_orders[i] << std::endl;
        }
        for (auto itr = bids.begin(); itr != bids.end(); ++itr) {
          std::cout << itr->first << '\t' << itr->second << '\n';
        }
        //std::cout << "Changes: " << changes << std::endl;
      } else if (type.compare("l2update") == 0) {
        // update order book
      } else {
        // subscribe message
      }
      

      // printf("%.*s\n",
      //   static_cast<int>(message->len()),
      //   static_cast<const char *>(message->payload()));
      break;
    }
    case RdKafka::ERR__PARTITION_EOF: // Last message
      if (exit_eof) {
        run = 0;
      }
      break;
    case RdKafka::ERR__UNKNOWN_TOPIC:
    case RdKafka::ERR__UNKNOWN_PARTITION:
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
      run = 0;
      break;
    default: // Error
      std::cerr << "Consume failed: " << message->errstr() << std::endl;
      run = 0;
  }
}

int main(int argc, char **argv) {
  std::string brokers = "localhost";
  std::string errstr;
  int64_t start_offset = RdKafka::Topic::OFFSET_BEGINNING;
  int opt;
  HashPartitionerCb hash_partitioner;

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
  conf_out->set("default_topic_conf", tconf_out, errstr);

  // Create producer using accumulated global configuration.
  RdKafka::Producer *producer = RdKafka::Producer::create(conf_out, errstr);
  if (!producer) {
    std::cerr << "Failed to create producer: " << errstr << std::endl;
    exit(1);
  }
  std::cout << "% Created producer " << producer->name() << std::endl;

  /* ============================== Run ============================== */
  while (run) {
    // Consume message
    RdKafka::Message *msg = consumer->consume(topic_in, partition_in, 1000);
    msg_consume(msg, NULL);

    // Produce message
    // RdKafka::Headers *headers = RdKafka::Headers::create();
    // headers->add("my header", "header value");
    // headers->add("other header", "yes");

    // std::string line = "produced message";
    // RdKafka::ErrorCode resp =
    //   producer->produce(topic_str_out, partition_out,
    //                     RdKafka::Producer::RK_MSG_COPY, // copy payload
    //                     const_cast<char *>(line.c_str()), line.size(),
    //                     NULL, 0, 0,
    //                     headers,
    //                     NULL);
    // if (resp != RdKafka::ERR_NO_ERROR) {
    //   std::cerr << "% Produce failed: " << RdKafka::err2str(resp) << std::endl;
    //   delete headers; // Headers are automatically deleted on produce() success.
    // } else {
    //   std::cerr << "% Produced message (" << line.size() << " bytes)" << std::endl;
    // }
    // producer->poll(0);

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
/usr/bin/clang++ -O3 -Wall preprocessor_v3.cpp -std=c++11 -lrdkafka++ -lpthread -lz -lstdc++ -ljsoncpp -o preprocessor_v3

Command:
./preprocessor_v3 -t raw2 -u processed -p 0
*/