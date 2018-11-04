
#FROM smizy/scikit-learn:0.18-alpine
FROM bencuk/python-scikit:0.18.1

ARG MODEL_VER=1.0.0

LABEL Name=batcomputer-api AppVersion=1.0.0 ModelVersion=${MODEL_VER}

RUN pip3 install flask

WORKDIR /app
ADD src .
ADD *.pkl ./

ENV SERVER_PORT 8000
EXPOSE 8000

CMD ["python3", "server.py"]
