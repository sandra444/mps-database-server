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
        touch-reload-production \
        nightly.sh \
        weekly.sh

    cd /home/mps/mps-database-server
    git fetch
    git reset --hard HEAD
    python manage.py migrate --all
    ./manage.py collectstatic --noinput

    cd /home/mps/mps-web-client
    git fetch
    git reset --hard HEAD

    touch /home/mps/touch-reload-production

}

reset_all
