#!/bin/sh

set -e

if [ -z "$HOSTNAME" ]; then
  echo "HOSTNAME environment variable is not set"
  exit 1;
fi

use_dummy_certificate() {
  if grep -q "/etc/letsencrypt/live/\${HOSTNAME}" "/etc/nginx/templates/policy.conf.template"; then
    echo "Switching Nginx to use dummy certificate for $1"
    sed -i "s|/etc/letsencrypt/live/\${HOSTNAME}|/etc/nginx/ssl/dummy/$1|g" "/etc/nginx/templates/policy.conf.template"
  fi
}

use_lets_encrypt_certificate() {
  if grep -q "/etc/nginx/ssl/dummy/$1" "/etc/nginx/templates/policy.conf.template"; then
    echo "Switching Nginx to use Let's Encrypt certificate for $1"
    sed -i "s|/etc/nginx/ssl/dummy/$1|/etc/letsencrypt/live/\${HOSTNAME}|g" "/etc/nginx/templates/policy.conf.template"
  fi
}

reload_nginx() {
  echo "Reloading Nginx configuration"
  nginx -s reload
}

wait_for_lets_encrypt() {
  until [ -d "/etc/letsencrypt/live/$1" ]; do
    echo "Waiting for Let's Encrypt certificates for $1"
    sleep 5s & wait ${!}
  done
  use_lets_encrypt_certificate "$1"
  /docker-entrypoint.d/20-envsubst-on-templates.sh
  reload_nginx
}

if [ ! -f /etc/nginx/sites/ssl/ssl-dhparams.pem ]; then
  mkdir -p "/etc/nginx/ssl"
  openssl dhparam -out /etc/nginx/ssl/ssl-dhparams.pem 2048
fi

domains_fixed=$(echo "$HOSTNAME" | tr -d \")
for domain in $domains_fixed; do
  echo "Checking configuration for $domain"

#  if [ ! -f "/etc/nginx/sites/$domain.conf" ]; then
#    echo "Creating Nginx configuration file /etc/nginx/sites/$domain.conf"
#    sed "s/\${domain}/$domain/g" /customization/site.conf.tpl > "/etc/nginx/sites/$domain.conf"
#  fi

  if [ ! -f "/etc/nginx/ssl/dummy/$domain/fullchain.pem" ]; then
    echo "Generating dummy ceritificate for $domain"
    mkdir -p "/etc/nginx/ssl/dummy/$domain"
    printf "[dn]\nCN=${domain}\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:$domain, DNS:www.$domain\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth" > openssl.cnf
    openssl req -x509 -out "/etc/nginx/ssl/dummy/$domain/fullchain.pem" -keyout "/etc/nginx/ssl/dummy/$domain/privkey.pem" \
      -newkey rsa:2048 -nodes -sha256 \
      -subj "/CN=${domain}" -extensions EXT -config openssl.cnf
    rm -f openssl.cnf
  fi

  if [ ! -d "/etc/letsencrypt/live/$domain" ]; then
    use_dummy_certificate "$domain"
    /docker-entrypoint.d/20-envsubst-on-templates.sh
    wait_for_lets_encrypt "$domain" &
  else
    use_lets_encrypt_certificate "$domain"
    /docker-entrypoint.d/20-envsubst-on-templates.sh
  fi
done

./docker-entrypoint.sh nginx -g "daemon off;"