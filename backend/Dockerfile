FROM python:3.11.4-slim-buster

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && \
    pip install Django==3.2.25 \
    psycopg2-binary>=2.9 \
    django-extensions \
    whitenoise==5.3.0 \
    djangorestframework==3.12.4 \
    django-environ==0.8.1 \
    django-cors-headers==3.10.0  \
    anyconfig==0.14.0 \
    requests==2.31.0 \
    pyOpenSSL==23.3.0 \
    channels==4.0.0 \
    daphne \
    pythonping \
    asgiref \
    channels_redis==4.0.0 \
    uvicorn[standard] 

RUN pip install gunicorn \
    hupper \
    hvac \
    watchfiles \
    subprocess.run \
    django-templates

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget netcat vim && \
    rm -rf /var/lib/apt/lists/*

RUN pip install django-extensions
RUN pip install boto3

RUN wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.3/mkcert-v1.4.3-linux-amd64 -O mkcert && \
    chmod +x mkcert && \
    mv mkcert /usr/local/bin/ && \
    mkcert -install && mkcert -key-file /etc/ssl/private/localhost.key -cert-file /etc/ssl/certs/localhost.pem localhost

#COPY ./backend/middleware.py 

#RUN mv localhost.pem /etc/ssl/certs/localhost.pem && \
#    mv localhost-key.pem /etc/ssl/private/localhost.key

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
