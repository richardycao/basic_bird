from pipeline import Pipeline

"""
How do you set up a Module?
The Dockerfile, requirements, and code are provided. I just need to link it to the pipeline.
To do that, just provide the path to the directory that includes the Dockerfile.
"""

p = Pipeline(
  ['./producer', './preprocessor', './predictor']
)
p.create()