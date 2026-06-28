FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MKTVIS_CONFIG_SOURCE=env

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        nginx \
        supervisor \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1000 mktvis \
 && useradd  --system --uid 1000 --gid mktvis --no-create-home --shell /usr/sbin/nologin mktvis

WORKDIR /app

COPY setup.py ./
COPY mktvis ./mktvis
COPY main.py ./
COPY docker/index.html.j2 /tmp/index.html.j2

RUN pip install --no-cache-dir jinja2 .

RUN mkdir -p /var/www/mktvis /var/log/supervisor /var/opt/mktvis \
 && chown -R mktvis:mktvis /var/www/mktvis /var/opt/mktvis /var/log/supervisor

COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]