FROM debian:latest

# Install OpenSSL to generate a self-signed certificate
RUN apt-get update && apt-get -y upgrade && apt-get install -y openssl \
    nginx \
    libmodsecurity3 \
    libnginx-mod-http-ndk \
    libnginx-mod-http-modsecurity \
    modsecurity-crs \
    curl && \
    apt-get clean

# Create SSL certificate and key
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx.key \
    -out /etc/ssl/certs/nginx.crt \
    -subj "/CN=42transcendence.com"

# Copy the Nginx configuration file
COPY default.conf /etc/nginx/conf.d/default.conf
COPY modsecurity.conf /etc/modsecurity/activated_rules

EXPOSE 8443

CMD ["nginx", "-g", "daemon off;"]