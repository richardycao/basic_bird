FROM tensorflow/tensorflow

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall hummingbird
RUN pip install --upgrade git+https://github.com/richardycao/hummingbird_python.git#egg=hummingbird

COPY test-strat-predict.py .
COPY settings.txt .
COPY params.json .

CMD ["python","./test-strat-predict.py"]
