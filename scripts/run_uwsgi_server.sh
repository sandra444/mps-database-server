#!/bin/bash

uwsgi --chdir=/home/mps/mps-database-server \
 --module=mps.wsgi:application  \
 --env DJANGO_SETTINGS_MODULE=mps.settings \
 --socket=127.0.0.1:8090 \
 --processes=16 \
 --daemonize=/home/mps/log/uwsgid.log \
 --touch-reload=/home/mps/touch-reload-production \
 --logto=/home/mps/log/mps.log
