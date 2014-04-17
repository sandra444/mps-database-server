!#/bin/sh

cd /home/mps/mps

# update compound activities that are not updated or older than 180 days
python manage.py runscript update_activities --script-args=180