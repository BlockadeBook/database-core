#!/bin/bash

APP_HOST=${HOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8080}

uvicorn app.main:app --reload --proxy-headers --host "$APP_HOST" --port "$APP_PORT"
