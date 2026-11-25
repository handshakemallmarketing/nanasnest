FROM caddy:2-alpine
RUN apk add --no-cache python3
COPY inquiry.py /opt/inquiry.py
COPY Caddyfile /etc/caddy/Caddyfile
COPY *.html robots.txt sitemap.xml /srv/
COPY assets /srv/assets
COPY areas /srv/areas
COPY services /srv/services
COPY blog /srv/blog
EXPOSE 8080

CMD ["sh","-c","python3 /opt/inquiry.py & exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile"]
