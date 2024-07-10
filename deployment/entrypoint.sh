#!/bin/sh
set -e

if [ "$MODE" = "app" ]; then
  statusmgr run -p $PORT -h $HOST
elif [ "$MODE" = "migrations" ]; then
  statusmgr db migrate
elif [ "$MODE" = "dev" ]; then
  statusmgr dev --docker
elif [ "$MODE" = "shell" ]; then
  $@
else
  echo "ERROR: \$MODE is not set to \"app\", \"migrations\", \"dev\" or \"shell\"."
  exit 1
fi
