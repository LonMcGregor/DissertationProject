rm db.sqlite3
rm -r student\migrations
rm -r notify\migrations
rm -r var
python3 manage.py makemigrations
python3 manage.py makemigrations student
python3 manage.py makemigrations teacher
python3 manage.py makemigrations notify
python3 manage.py migrate
python3 manage.py collectstatic
