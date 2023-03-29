FROM nginx:1.21-alpine

COPY ./nginx.conf /nginx.conf.template
COPY ./nginx_root.conf /nginx_root.conf.template

COPY ./docker-entrypoint.sh /docker-entrypoint.d/
