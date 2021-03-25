

class PythonOperator(object):
  def __init__(self, 
    function,           # Python function
    priority: int,      # 1 is highest, 5 is lowest
    input_queue: str,
    output_queue: str,
    input_server: str,
    output_server: str,
    params: dict):      # function parameters

    self.function = function
    self.priority = priority
    self.input_queue = input_queue
    self.output_queue = output_queue
    self.input_server = input_server
    self.output_server = output_server
    self.params = params

class DAG(object):
  def __init__(self, sequence):
    self.jobs = [s for s in sorted(sequence, key=lambda x: x[1])] # sort by priority. 1 = highest, 5 = lowest

  def run(self):
    for j in jobs:
      j.start()
