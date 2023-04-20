FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

ADD mtprotopy.py /

RUN pip install --no-cache-dir uvloop cryptography toml

ENTRYPOINT [ "python3", "mtprotopy.py" ]
