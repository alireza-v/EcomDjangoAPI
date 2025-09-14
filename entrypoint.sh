#!/bin/sh

# exit on error
set -e

python manage.py migrate --noinput

python manage.py collectstatic --noinput

# execute CMD
exec "$@"
