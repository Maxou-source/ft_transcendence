FROM alpine:3.14

# Create a user and group for Vault
RUN addgroup -S vault && adduser -S vault -G vault

# Modify apk repositories to use HTTP instead of HTTPS
RUN sed -i 's/https/http/' /etc/apk/repositories

# Install dependencies
RUN apk update && apk add --no-cache \
    curl \
    libc6-compat \
    libcap \
    ca-certificates \
    openssl \
    unzip

RUN apk add --no-cache bash curl jq

# Create necessary directories
RUN mkdir -p /vault/config /vault/data /vault/keys /vault/root && \
    chown -R vault:vault /vault

# Download and install Vault
ENV VAULT_VERSION="1.10.0"
RUN curl -fsSL https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip -o vault.zip && \
    unzip -o vault.zip -d /tmp && \
    mv /tmp/vault /usr/bin/vault && \
    rm vault.zip && \
    chmod +x /usr/bin/vault

# Copy Vault configuration
COPY ./config/config.hcl /vault/config

# Expose the Vault port (default is 8200)
EXPOSE 8200

# Switch to non-root user
USER root
# Copy the auto-init script to the container
COPY ./init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

# Entry point to auto-init Vault
ENTRYPOINT ["/usr/local/bin/init.sh"]

