
#FROM smizy/scikit-learn:0.18-alpine
FROM bencuk/python-scikit:0.18.1

ARG VERSION=1.0.0

LABEL Name=batcomputer-api AppVersion=1.0.0 ModelVersion=${VERSION}

RUN pip3 install flask
RUN pip3 install flask-swagger-ui

WORKDIR /app
ADD src .
ADD *.pkl ./

ENV SERVER_PORT 8000
EXPOSE 8000

CMD ["python3", "server.py"]
