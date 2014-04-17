!#/bin/sh

TODAY=$(date +"%Y-%m-%d")

cd /home/mps/mps

# delete dumps older than 14 days
find /data/backup/home/mps/dbdump* -mtime +14 -exec rm {} \;

# create a dump with time-stamp
pg_dump mpsdb | gzip > /data/backup/home/mps/dbdump_$TODAY.sql.gz

# backup project files, in particular migrations
unison -root /home/mps/mps/ -root /data/backup/home/mps/mps/ -force=/home/mps/mps/ -batch -log=false -backuploc=local -maxbackups=5