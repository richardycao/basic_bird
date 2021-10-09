from hummingbird import Module2
import sys

class MessageLogger(Module2):
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            while True:
                message = self.receive()

                if message is not None:
                    print(message)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
  c = MessageLogger()
  c.run()