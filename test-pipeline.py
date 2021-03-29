from hummingbird import Pipeline, PipelineNode

"""
Documentation

params:
  servers-in and servers-out: To run it on Docker, leave it blank - it is
    set to 'kafka0:29092' by default, which is configured to be Docker.
    To run it locally, set it to 'localhost:9092', then build the pipeline 
    by calling pipeline.build(). Copy the command generated in the Dockerfile 
    and manually run it locally after kafka has started. Keep in mind all the 
    dependencies need to be installed for it to run locally.
"""

if __name__ == "__main__":
  p = Pipeline(id='test1', modules=[
    PipelineNode(
      module_path="./modules-python/cbp-websocket/cbp-websocket.py",
      params={
        "product_ids": 'BTC-USD',
        "channels": 'ticker',
        # "servers-out": 'localhost:9092'
      }
    ),
    PipelineNode(
      module_path="./modules-python/cbp-websocket-processor/cbp-websocket-processor.py",
      params={
        "type": 'ticker',
        "bar-type": 'tick',
        # "servers-in": 'localhost:9092',
        # "servers-out": 'localhost:9092'
      }
    ),
    PipelineNode(
      module_path="./modules-python/message-logger/message-logger.py",
      params={
        # "servers-in": 'localhost:9092',
      }
    ),
  ])
  p.build()