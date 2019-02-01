ARG PYTHON_VERSION=3.5.6
FROM python:${PYTHON_VERSION}-slim-stretch

# Model version, not critical it is correct, used for status reporting
ARG VERSION=1.0.0

LABEL Name=batcomputer-api AppVersion=2.2.0 ModelVersion=${VERSION}

# Install Python requirements
ADD requirements.txt .
RUN pip3 install -r requirements.txt

# Add in our app and the pickle files
WORKDIR /app
ADD src .
ADD pickles/*.pkl ./pickles/

# Runtime configuration & settings
ENV VERSION $VERSION
ENV GUNICORN_CMD_ARGS "--bind=0.0.0.0:8000"
EXPOSE 8000

# Start the app via Gunicorn WSGI server
CMD ["gunicorn", "--access-logfile", "-", "server"]
#CMD ["python3", "server.py"]