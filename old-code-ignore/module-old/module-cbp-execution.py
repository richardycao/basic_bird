# python3.7 module-cbp-execution.py -i moving-average-trades -s kafka0:29092

from module-old import Module
from confluent_kafka import Producer, Consumer, KafkaException
import json
from json import loads, dumps
import sys

class ModuleCBPExecution(Module):
    def __init__(self, args):
        super().__init__(args)

    def run(self):
        pass

# if __name__ == "__main__":
#     m = ModuleCBPExecution(sys.argv[1:])
#     m.run()