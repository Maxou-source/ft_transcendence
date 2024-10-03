#!/bin/sh

export DJANGO_SETTINGS_MODULE=app.settings

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL started"
fi

python manage.py reset_db --no-input
python manage.py watchstatic &
python manage.py makemigrations --noinput
python manage.py migrate --noinput
if [ $(python -c "import django; django.setup(); from django.contrib.auth.models import User; print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())") = "False" ]; then
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME
    echo "Superuser created"
else
    echo "Superuser already exists"
fi

exec gunicorn app.asgi:application \
  --certfile /etc/ssl/certs/localhost.pem \
  --keyfile /etc/ssl/private/localhost.key \
  -b 0.0.0.0:8000 \
  -k uvicorn.workers.UvicornWorker
