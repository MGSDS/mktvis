#!/bin/sh
set -eu

export MKTVIS_HOME_LAT="${MKTVIS_HOME_LAT:-54.3109861}"
export MKTVIS_HOME_LON="${MKTVIS_HOME_LON:-10.1296693}"
export MKTVIS_BACKEND_URL="${MKTVIS_BACKEND_URL:-http://127.0.0.1:5555}"
export MKTVIS_LISTEN_PORT="${MKTVIS_LISTEN_PORT:-80}"

DB_DIR="${MKTVIS_DB_DIR:-/var/opt/mktvis}"
LICENSE_KEY="${MAXMIND_LICENSE_KEY:-}"

mkdir -p /var/www/mktvis /var/log/supervisor /var/opt/mktvis

python -c "
import os
tmpl = open('/tmp/nginx.index.html').read()
open('/var/www/mktvis/index.html', 'w').write(tmpl.format(
    MKTVIS_HOME_LAT=os.environ['MKTVIS_HOME_LAT'],
    MKTVIS_HOME_LON=os.environ['MKTVIS_HOME_LON'],
    MKTVIS_BACKEND_URL=os.environ['MKTVIS_BACKEND_URL'],
))
" && chown mktvis:mktvis /var/www/mktvis/index.html

python -c "
import os
tmpl = open('/tmp/nginx.conf').read()
open('/etc/nginx/nginx.conf', 'w').write(tmpl.format(
    MKTVIS_LISTEN_PORT=os.environ['MKTVIS_LISTEN_PORT'],
))
"

mkdir -p "$DB_DIR"

if [ -n "$LICENSE_KEY" ]; then
    for edition in GeoLite2-City GeoLite2-ASN; do
        target="$DB_DIR/${edition}.mmdb"
        if [ ! -f "$target" ] || [ "${MKTVIS_FORCE_DB_UPDATE:-0}" = "1" ]; then
            echo "[entrypoint] downloading $edition ..."
            tmp=$(mktemp -d)
            curl -fsSL \
                "https://download.maxmind.com/app/geoip_download?edition_id=${edition}&license_key=${LICENSE_KEY}&suffix=tar.gz" \
                -o "$tmp/db.tar.gz"
            tar -xzf "$tmp/db.tar.gz" -C "$tmp" --strip-components=1
            install -m 0644 "$tmp/${edition}.mmdb" "$target"
            rm -rf "$tmp"
        fi
    done
else
    echo "[entrypoint] MAXMIND_LICENSE_KEY not set; expecting DBs to be mounted at $DB_DIR" >&2
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf