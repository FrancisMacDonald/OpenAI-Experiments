FROM alpine:latest as base
LABEL maintainer="Francis MacDonald <francis@francism.ca>"
LABEL version="0.0.1"

RUN apk add --no-cache python3 py3-pip && \
    rm -rf /var/cache/apk/*

COPY requirements.txt requirements.txt
COPY Bots/ Bots/
COPY Games/ Games/
COPY main.py main.py

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    rm -rf /root/.cache/pip/*

CMD [ "python", "main.py" ]