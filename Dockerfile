FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY *.html robots.txt sitemap.xml /srv/
COPY assets /srv/assets
COPY areas /srv/areas
COPY services /srv/services
COPY blog /srv/blog
EXPOSE 8080
