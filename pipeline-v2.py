from hummingbird import Pipeline2, Node

if __name__ == "__main__":
  # pipeline = Pipeline2(
  #   id = "pipeline-v2",
  #   nodes = [
  #     Node(
  #       id='binance-websocket',
  #       path='./modules-useless/binance-websocket/binance-websocket.py',
  #       params={
  #         'params': ['btcusdt@aggTrade']
  #       },
  #       # outputs=['logger']
  #     ),
  #     Node(
  #       id='logger',
  #       path='./modules-useless/logger/logger.py',
  #       params={},
  #       inputs=['binance-websocket']
  #     )
  #   ]
  # )

  # pipeline = Pipeline2(
  #   id = "pipeline-v2",
  #   nodes = [
  #     Node(
  #       id="cbp-websocket",
  #       path="./modules-useless/cbp-websocket/cbp-websocket.py",
  #       params={
  #         "product_ids": ["DOGE-USD"],
  #         "channels": ['level2'],
  #         # "servers_in": 'localhost:9092',
  #         # "servers_out": 'localhost:9092'
  #       },
  #       outputs=['doge-job']
  #     ),
  #     Node(
  #       id="doge-job",
  #       path="./modules-useless/doge-job/doge-job.py",
  #       params={
  #         # "servers_in": 'localhost:9092',
  #         # "servers_out": 'localhost:9092'
  #       },
  #       inputs=['cbp-websocket']
  #     ),
  #   ]
  # )

  pipeline = Pipeline2(
    id = "pipeline-v2",
    nodes = [
      Node(
        id="cbp-websocket",
        path="./modules-useless/cbp-websocket/cbp-websocket.py",
        params={
          "product_ids": ["DOGE-USD"],
          "channels": ['level2'],
        },
        outputs=['order-book-features']
      ),
      Node(
        id="order-book-features",
        path="./modules-useless/order-book-features/order-book-features.py",
        params={
          'max_non_decimal_digits': 1,
          'max_decimal_digits': 4
        },
        inputs=['cbp-websocket'],
        outputs=['strategy']
      ),
      Node(
        id="strategy",
        path="./modules-useless/strategy/strategy.py",
        params={},
        inputs=['order-book-features'],
      ),
    ]
  )
  pipeline.build()