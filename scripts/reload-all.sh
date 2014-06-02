#!/bin/bash

function reset_all () {

    cd /home/mps

    DATE=`date +%Y-%m-%d-%H-%M-%S`

    pg_dump -Fc mpsdb > mpsdb.pg

    zip -r "backup/full_backup-$DATE.zip" \
        mps_credentials.py \
        mps-database-server \
        mpsdb.pg \
        mpsdemo \
        autorun_mps.sh \
        mps-web-client \
        nginx.conf \
        reload_all.sh \
        touch-reload-production

    cd /home/mps/mps-database-server
    git reset --hard HEAD
    git fetch
    git pull
    git reset --hard HEAD
    python manage.py migrate --all

    cd /home/mps/mps-web-client
    git reset --hard HEAD
    git fetch
    git pull
    git reset --hard HEAD

    touch /home/mps/touch-reload-production

}

reset_all
