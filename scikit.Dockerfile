
# Use some ARGs to change versions at build time
# There's three versions we're juggling here, Alpine, Python and Scikit-Learn
# We assume Alpine = v3.7
ARG PYTHON_VERSION=3.6.3
FROM python:${PYTHON_VERSION}-alpine3.7

ARG SCIKIT_VERSION=0.18.1

# Enable community package repo and update
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.7/community' >> /etc/apk/repositories
RUN apk update
RUN pip3 install --upgrade pip
 
# Base stuff
RUN apk --no-cache add openblas libstdc++
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

# Cleanup (saves a couple of MB)
RUN apk del .builddeps
RUN find /usr/local/lib/python3.6 -name __pycache__ | xargs rm -r
RUN rm -rf \
    /root/.[acpw]* \
    ipaexg00301* \