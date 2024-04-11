# Dockerfile

FROM nginx:latest

ADD policy.conf.template /etc/nginx/templates/policy.conf.template
ADD options-ssl-nginx.conf /etc/nginx/ssl/options-ssl-nginx.conf

COPY nginx.sh /customization/

RUN chmod +x /customization/nginx.sh

EXPOSE 80

CMD ["/customization/nginx.sh"]