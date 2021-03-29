from hummingbird import Module
import sys

"""
Documentation for MessageLogger

Description: Logs incoming messages.

Parameters:
    None.

Message Format:
    Input: Anything
    Output: None

Command:
    python3 message-logger.py
    e.g. python3 message-logger.py

"""

class MessageLogger(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(False)

        self.build()

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
  c = MessageLogger(sys.argv[1:])
  c.run()
