ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}-slim-stretch

LABEL Name=batcomputer-api AppVersion=3.1

# Install Python requirements
ADD requirements.txt .
RUN pip3 install -r requirements.txt

# Add in our app and the pickle & metadata files
WORKDIR /app
ADD src ./src/
ADD pickles/*.pkl ./pickles/
ADD pickles/*.json ./pickles/

# Runtime configuration & settings
ENV VERSION $VERSION
EXPOSE 8000

# Start the app via Gunicorn WSGI server
CMD ["gunicorn", "--bind=0.0.0.0", "--access-logfile", "-", "--chdir", "src", "server"]
#CMD ["python3", "src/server.py"]