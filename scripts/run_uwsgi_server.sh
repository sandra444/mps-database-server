#!/bin/bash

uwsgi --chdir=/home/mps/mps-database-server \
 --module=mps.wsgi:application  \
 --env DJANGO_SETTINGS_MODULE=mps.settings \
 --socket=127.0.0.1:8090 \
 --processes=16 \
 --harakiri=300 \
 --max-requests=9000 \
 --vacuum \
 --daemonize=/home/mps/log/mps.log \
 --threads 2 \
 --master \
 --touch-reload=/home/mps/touch-reload-production \
 --thunder-lock \
 --post-buffering 1

