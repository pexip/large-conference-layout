#!/bin/bash

set -e

trap exit INT TERM

if [ -z "$HOSTNAME" ]; then
  echo "HOSTNAME environment variable is not set"
  exit 1;
fi

until nc -z nginx 80; do
  echo "Waiting for nginx to start..."
  sleep 5s & wait ${!}
done

if [ "$CERTBOT_TEST_CERT" != "0" ]; then
  test_cert_arg="--test-cert"
fi

domains_fixed=$(echo "$HOSTNAME" | tr -d \")
echo "$domains_fixed"
domain_list=($domains_fixed)
emails_fixed=$(echo "$CERTBOT_EMAIL" | tr -d \")
emails_list=($emails_fixed)
for i in "${!domain_list[@]}"; do
  domain="${domain_list[i]}"

  mkdir -p "/var/www/certbot/$domain"

  if [ -d "/etc/letsencrypt/live/$domain" ]; then
    echo "Let's Encrypt certificate for $domain already exists"
    continue
  fi

  email="${emails_list[i]}"
  if [ -z "$email" ]; then
    email_arg="--register-unsafely-without-email"
    echo "Obtaining the certificate for $domain without email"
  else
    email_arg="--email $email"
    echo "Obtaining the certificate for $domain with email $email"
  fi

  echo "webroot /var/www/certbot/$domain"
  
  certbot certonly \
    --webroot \
    -w "/var/www/certbot/$domain" \
    -d "$domain" \
    $test_cert_arg \
    $email_arg \
    --rsa-key-size "${CERTBOT_RSA_KEY_SIZE:-4096}" \
    --agree-tos \
    --noninteractive \
    --verbose || true
done