from hummingbird import Pipeline, PipelineNode

if __name__ == "__main__":
  p = Pipeline([
    PipelineNode(
      module_path="./modules-python/cbp-websocket/cbp-websocket.py",
      params={
        "product_ids": 'BTC-USD',
        "channels": 'ticker',
      }
    ),
    PipelineNode(
      module_path="./modules-python/cbp-websocket-processor/cbp-websocket-processor.py",
      params={}
    ),
  ])
  p.build()