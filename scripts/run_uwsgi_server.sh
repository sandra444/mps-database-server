#!/bin/bash

uwsgi --chdir=/home/mps/mps-database-server \
 --module=mps.wsgi:application  \
 --env DJANGO_SETTINGS_MODULE=mps.settings \
 --socket=127.0.0.1:8090 \
 --processes=32 \
 --daemonize=/home/mps/log/uwsgid.log
