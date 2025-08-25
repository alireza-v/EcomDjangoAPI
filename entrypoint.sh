#!/bin/sh
set -e # Exit execution if failed

python manage.py migrate # Apply django database migrations

exec "$@" # Execute CMD from Dockerfile if exists
