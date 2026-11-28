FROM caddy:2-alpine
RUN apk add --no-cache python3
COPY inquiry.py /opt/inquiry.py
COPY Caddyfile /etc/caddy/Caddyfile
COPY *.html robots.txt sitemap.xml llms.txt /srv/
COPY assets /srv/assets
COPY areas /srv/areas
COPY services /srv/services
COPY blog /srv/blog
ARG RAILWAY_GIT_COMMIT_SHA=unknown
RUN printf '%s\n' "$RAILWAY_GIT_COMMIT_SHA" > /srv/release.txt
EXPOSE 8080

CMD ["sh","-c","python3 /opt/inquiry.py & exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile"]
