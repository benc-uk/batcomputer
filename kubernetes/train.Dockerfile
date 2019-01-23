
#FROM smizy/scikit-learn:0.18-alpine
FROM bencuk/python-scikit:0.18.1

ARG VERSION=1.0.0

LABEL Name=batcomputer-train-job AppVersion=1.0.0 ModelVersion=${VERSION}

#RUN wget https://github.com/sgerrand/alpine-pkg-py-pandas/releases/download/0.20.3-r0/py3-pandas-0.20.3-r0.apk
#RUN apk add --allow-untrusted py3-pandas-0.20.3-r0.apk
RUN apk add --update g++
RUN pip3 install pandas
RUN pip3 install python-dotenv
RUN apk add libffi-dev openssl-dev
RUN pip3 install azure-storage

# Add in our app and the pickle files
WORKDIR /job
ADD notebooks/scikit-titanic-local.py .
ADD data/train.csv ./data/train.csv

# Runtime configuration & settings
ENV VERSION $VERSION

CMD ["python3", "scikit-titanic-local.py"]