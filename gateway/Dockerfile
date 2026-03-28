FROM nginx:1.25-alpine

# envsubst is included in alpine's gettext package
RUN apk add --no-cache gettext

COPY nginx.conf /etc/nginx/templates/default.conf.template

# nginx docker image automatically runs envsubst on files in /etc/nginx/templates/
# and outputs them to /etc/nginx/conf.d/ at container start