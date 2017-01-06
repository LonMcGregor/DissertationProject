del db.sqlite3
del student\migrations
del notify\migrations
python manage.py makemigrations
python manage.py makemigrations student
python manage.py makemigrations teacher
python manage.py makemigrations notify
python manage.py migrate
