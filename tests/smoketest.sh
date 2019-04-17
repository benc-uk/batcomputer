#!/bin/bash

wget -O- http://$API_HOST/api/info
if [ $? -ne 0 ]; then
  exit 500
fi

wget -O- http://$API_HOST/swagger.json
if [ $? -ne 0 ]; then
  exit 500
fi

wget -O- http://$API_HOST/api/predict/params
if [ $? -ne 0 ]; then
  exit 500
fi