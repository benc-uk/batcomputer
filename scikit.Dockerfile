FROM python:alpine3.6

ARG SCIKIT_VERSION=0.18

RUN apk update
RUN pip3 install --upgrade pip

RUN apk --no-cache add --virtual .builddeps \
    build-base \
    freetype-dev \
    gfortran \
    openblas-dev \
    pkgconf \
    python3-dev
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install scikit-learn==${SCIKIT_VERSION}