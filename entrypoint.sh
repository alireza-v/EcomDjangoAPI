#!/bin/sh
set -e

python <<END
import os, time, psycopg2
from psycopg2 import OperationalError

while True:
    try:
        conn = psycopg2.connect(
            host="db",
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            dbname=os.environ["POSTGRES_DB"],
        )
        conn.close()
        break
    except OperationalError:
        time.sleep(2)
END


python <<END
import time, redis

while True:
    try:
        r = redis.Redis(host="redis", port=6379, db=0)
        r.ping()
        break
    except redis.exceptions.ConnectionError:
        time.sleep(2)
END


python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec "$@"
