from hummingbird import Pipeline, PipelineNode

if __name__ == "__main__":
  p = Pipeline(id='pipeline-v1', modules=[
    PipelineNode(
      module_path="./modules-python/cbp-historic-rates/cbp-historic-rates.py",
      params={
        "start": "2021-02-08T00:00:00.000Z",
        "stop": "2021-04-07T00:00:00.000Z",
        # "servers-out": 'localhost:9092'
      }
    ),
    PipelineNode(
      module_path="./temp/test-strat-process/test-strat-process.py",
      params={
        'durations': "5,30",
        # "servers-in": 'localhost:9092'
        # "servers-out": 'localhost:9092'
      }
    ),
    PipelineNode(
      module_path="./temp/test-strat-predict/test-strat-predict.py",
      params={
        'currency': 'BTC',
        # "servers-in": 'localhost:9092'
      }
    ),
  ])
  p.build()