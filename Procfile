release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn ethara.wsgi --log-file -
