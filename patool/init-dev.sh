#!/usr/bin/env bash
rm db.sqlite3
rm -r common/migrations feedback/migrations var
./manage.py makemigrations common feedback
./manage.py migrate
./manage.py collectstatic --noinput
./manage.py shell -c "
from test.prepare_database import prepare_database
prepare_database()
"