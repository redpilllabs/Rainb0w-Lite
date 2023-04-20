FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

ADD mtprotopy.py /

RUN apk update \
    && apk add build-base

RUN pip install -U setuptools pip

RUN pip install --no-cache-dir uvloop cryptography toml

ENTRYPOINT [ "python3", "mtprotopy.py" ]
