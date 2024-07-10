#!/bin/sh
set -e

if [ "$MODE" = "app" ]; then
  pwstorage run -p $PORT -h $HOST
elif [ "$MODE" = "migrations" ]; then
  pwstorage db migrate
elif [ "$MODE" = "dev" ]; then
  pwstorage dev --docker
elif [ "$MODE" = "shell" ]; then
  $@
else
  echo "ERROR: \$MODE is not set to \"app\", \"migrations\", \"dev\" or \"shell\"."
  exit 1
fi
