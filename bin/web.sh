#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

if [ -z ${PORT+x} ]; then
	PORT=80
fi
if [ -z ${WEB_WORKERS+x} ]; then
	WEB_WORKERS=4
fi
if [ -z ${TIMEOUT+x} ]; then
	TIMEOUT=1000
fi
OPTS="--bind=0.0.0.0:$PORT --chdir=/app/ --log-file - --access-logfile - --workers=$WEB_WORKERS --timeout=$TIMEOUT"
if [[ $(echo $DEBUG | tr a-z A-Z) = "TRUE" ]]; then
	OPTS="$OPTS --reload"
fi

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi $OPTS
