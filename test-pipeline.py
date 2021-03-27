from hummingbird import Pipeline, PipelineNode

if __name__ == "__main__":
  p = Pipeline(id='test1', modules=[
    PipelineNode(
      module_path="./modules-python/cbp-websocket/cbp-websocket.py",
      params={
        "product_ids": 'BTC-USD',
        "channels": 'ticker',
        #"servers-out": 'localhost:9092'
      }
    ),
    PipelineNode(
      module_path="./modules-python/cbp-websocket-processor/cbp-websocket-processor.py",
      params={
        #"servers-in": 'localhost:9092',
        #"servers-out": 'localhost:9092'
      }
    ),
  ])
  p.build()