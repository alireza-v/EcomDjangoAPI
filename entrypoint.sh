#!/bin/sh
set -e # Exit execution if failed

python manage.py migrate

exec "$@" # Execute CMD from Dockerfile if exists
