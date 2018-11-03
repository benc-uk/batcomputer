
FROM smizy/scikit-learn:0.18-alpine
#FROM bencuk/python-scikit:0.18

LABEL Name=scikit-pickle-api Version=1.0.0

RUN pip3 install flask

WORKDIR /app
ADD *.py ./
ADD *.pkl ./

ENV SERVER_PORT 8000
EXPOSE 8000

CMD ["python3", "server.py"]
