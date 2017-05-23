#!/usr/bin/env bash
rm db.sqlite3
rm -r common/migrations
rm -r feedback/migrations
rm -r var
python3 manage.py makemigrations
python3 manage.py makemigrations common
python3 manage.py makemigrations feedback
python3 manage.py migrate
python3 manage.py collectstatic
