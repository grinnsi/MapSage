#!/bin/bash

set -e

if [ "$APP_ENV" = "dev" ]; then
    echo "Development environment detected."
    export APP_DEBUG_MODE="True"
    pip install --quiet debugpy || echo "Failed to install debugpy"

    python -u -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m server
else
    echo "Production environment detected."
    export APP_DEBUG_MODE="False"

    python -u -m server
fi

exec "$@"