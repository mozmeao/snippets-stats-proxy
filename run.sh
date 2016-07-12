#!/bin/bash
gunicorn proxy:application \
         --bind 0.0.0.0:${PORT:-8000} \
         --workers ${WEB_CONCURRENCY:-2} \
         --worker-class aiohttp.worker.GunicornWebWorker
