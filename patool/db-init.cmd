@echo off
del /s db.sqlite3
del /q /s student\migrations\*
del /q /s notify\migrations\*
del /q /s var\*
python manage.py makemigrations
python manage.py makemigrations student
python manage.py makemigrations teacher
python manage.py makemigrations notify
python manage.py migrate
python manage.py collectstatic
