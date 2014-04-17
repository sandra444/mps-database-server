.PHONY: help demo dump start pid reset collect fullload gitreset autoschema settings

help:
	@echo "Please use \`make <cmd>' where <cmd> is one of"
	@echo "  backup 	dump db and backup media into /data/backup/"
	@echo "  collect	collect static files"
	@echo "  demo		run demo server"
	@echo "  dump		dump data into json files"
	@echo "  load		load data from json files"
	@echo "  pid		lists server process"
	@echo "  start		run production server"
	@echo "  reset   	reset developer database"

backup:
	pg_dump mpsdb | gzip > /data/backup/home/mps/dbdump.sql.gz
	unison -root /home/mps/mps/ -root /data/backup/home/mps/mps/ -force=/home/mps/mps/ -batch -log=false

demo:
	./manage.py runserver

pid:
	netstat -tulpn | grep 8090

start:
	./manage.py run_gunicorn -b 127.0.0.1:8090

dump:
	mkdir -p datadumps
	for app in `ls */models.py`; do ./manage.py dumpdata `dirname $$app` > datadumps/`dirname $$app`.json; done
	./manage.py dumpdata auth contenttypes > datadumps/auth_contenttypes.json

load:
	./manage.py loaddata --ignorenonexistent datadumps/auth_contenttypes.json
	./manage.py loaddata --ignorenonexistent datadumps/compounds.json
	./manage.py loaddata --ignorenonexistent datadumps/bioactivities.json
	./manage.py loaddata --ignorenonexistent datadumps/cellsamples.json
	./manage.py loaddata --ignorenonexistent datadumps/drugtrials.json
	./manage.py loaddata --ignorenonexistent datadumps/microplates.json
	./manage.py loaddata --ignorenonexistent datadumps/microdevices.json


reset:
	rm mps_devel.db
	./manage.py syncdb

collect:
	./manage.py collectstatic

fullload:
	dropdb mpsdb || true
	echo "CREATE DATABASE mpsdb ENCODING 'UTF8' OWNER mps_database" | psql -d postgres
	echo "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mps_database" | psql -d postgres

	find . | grep "migrations/" | xargs -I{} rm -fv {}

	./manage.py syncdb

	./manage.py schemamigration assays --initial
	./manage.py schemamigration compounds --initial
	./manage.py schemamigration bioactivities --initial
	./manage.py schemamigration cellsamples --initial
	./manage.py schemamigration drugtrials --initial
	./manage.py schemamigration microdevices --initial
	./manage.py migrate --fake

	./manage.py loaddata --ignorenonexistent datadumps/auth_contenttypes.json
	./manage.py loaddata --ignorenonexistent datadumps/cellsamples.json
	./manage.py loaddata --ignorenonexistent datadumps/compounds.json
	./manage.py loaddata --ignorenonexistent datadumps/microdevices.json
	./manage.py loaddata --ignorenonexistent datadumps/assays.json
	./manage.py loaddata --ignorenonexistent datadumps/bioactivities.json
	./manage.py loaddata --ignorenonexistent datadumps/drugtrials.json

gitreset:
	git pull origin/master
	git reset --hard HEAD

autoschema:
	./manage.py schemamigration assays --auto || true
	./manage.py schemamigration compounds --auto || true
	./manage.py schemamigration bioactivities --auto || true
	./manage.py schemamigration cellsamples --auto || true
	./manage.py schemamigration drugtrials --auto || true
	./manage.py schemamigration microdevices --auto || true
	./manage.py migrate || true

settings:
	ln -s ../mps_credentials.py mps_credentials.py || true
