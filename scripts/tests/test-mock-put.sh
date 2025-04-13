#!/bin/bash

APP_PORT=${APP_PORT:-8080}

curl -X "PUT" \
  "http://localhost:$APP_PORT/records/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
  "data": "string"
}'
