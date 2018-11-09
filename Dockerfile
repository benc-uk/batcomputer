
#FROM smizy/scikit-learn:0.18-alpine
FROM bencuk/python-scikit:0.18.1

# Model version, not critical it is correct, used for status reporting
ARG VERSION=1.0.0

LABEL Name=batcomputer-api AppVersion=1.0.0 ModelVersion=${VERSION}

# Install Python requirements
ADD requirements.txt .
RUN pip3 install -r requirements.txt

# Add in our app and the pickle files
WORKDIR /app
ADD src .
ADD *.pkl ./

# Runtime configuration & settings
#ENV SERVER_PORT 8000
ENV VERSION $VERSION
EXPOSE 80

# Start the app via Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--access-logfile", "-", "server"]
#CMD ["python3", "server.py"]