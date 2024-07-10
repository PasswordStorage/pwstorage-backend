#!/bin/sh
set -e

# Check $MODE is set to "app"
# If true, check API server is running
if [ "$MODE" = "app" ]; then
  URL="http://localhost:$PORT/api/v1/ping/"

  export ANSWER=$(curl -s "$URL")

  if [ "$ANSWER" = '{"ok":true}' ]; then
    echo "OK"
    exit 0
  else
    echo "ERROR"
    exit 1
  fi
fi
