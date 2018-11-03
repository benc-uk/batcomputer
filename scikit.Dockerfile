FROM python:alpine3.6

# Can change version at build time
ARG SCIKIT_VERSION=0.18

# Update
RUN apk update
RUN pip3 install --upgrade pip

# Base stuff
RUN apk --no-cache add --virtual .builddeps \
    build-base \
    freetype-dev \
    gfortran \
    openblas-dev \
    pkgconf \
    python3-dev

# Python packages
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install scikit-learn==${SCIKIT_VERSION}

# Cleanup
RUN apk del .builddeps
RUN find /usr/local/lib/python3.6 -name __pycache__ | xargs rm -r
RUN rm -rf \
    /root/.[acpw]* \
    ipaexg00301* \