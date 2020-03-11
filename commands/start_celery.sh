#!/bin/bash

rm srv/project/run/celery.pid
rm srv/project/src/celerybeat.pid
celery -A currency_exchange worker -l info --workdir=/srv/project/src --pidfile=/srv/project/run/celery.pid

