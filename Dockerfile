
#FROM python:alpine3.6
FROM smizy/scikit-learn:0.18-alpine

LABEL Name=batcomputer Version=0.0.1

WORKDIR /app
ADD *.py ./
ADD docker_requirements.txt ./
ADD *.pkl ./

ENV APP_PORT 8000

#RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
#RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN python3 -m pip install -r docker_requirements.txt

EXPOSE 8000
CMD ["python3", "app.py"]
