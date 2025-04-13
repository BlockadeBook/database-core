#!/bin/bash

APP_PORT=${APP_PORT:-8080}

curl -d "" -X GET "http://localhost:$APP_PORT/records/all"