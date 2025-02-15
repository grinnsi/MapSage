#!/bin/bash

set -e

if [ "$APP_ENV" = "dev" ]; then
    echo "Development environment detected."
    export APP_DEBUG_MODE="True"
else
    echo "Production environment detected."
    export APP_DEBUG_MODE="False"
fi

exec "$@"