# python3.7 module-moving-average-predictor.py -i preprocessed-level2 -o moving-average-trades -s kafka0:29092 -t kafka0:29092

from module import Module
from confluent_kafka import Producer, Consumer, KafkaException
import json
from json import loads, dumps
import sys

class ModuleMovingAveragePredictor(Module):
    def __init__(self, args):
        super().__init__(args)

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    print(msg.value().decode("utf-8"))
                    decision = 0

                    # self.producer.produce(self.topic_out, value=dumps(decision).encode('utf-8'), callback=self.delivery_callback)
                    # self.producer.poll(0)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

# if __name__ == "__main__":
#     m = ModuleMovingAveragePredictor(sys.argv[1:])
#     m.run()