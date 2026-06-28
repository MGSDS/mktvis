# Live plot open connections from your Mikrotik device on a 3-dimensional globe

A Python module to export and visualize open connections from any Mikrotik RouterOS device.
It fetches connections via the RouterOS API, enriches them with geolocation data, and
renders them on an interactive 3D globe served by an embedded nginx frontend.

![example image](./img/screen.png)

## Disclaimer

IP geolocation data is inherently inaccurate and should be considered a rough guess.
Since data is retrieved via the RouterOS API, take appropriate precautions:

- use HTTPS / SSL to the router
- choose a strong password
- secure the host running the service

## What is the purpose?

One can argue that the added value of this project is limited. Ultimately, this is only a
(pretty) visualization of one's IP connections. But the visualization can be used vividly
demonstrate how interconnected modern devices are today. In my family, which does not have
a particular affinity for technology, I was able to generate some amazement. Evidently, not
everyone was aware that our smart helpers are constantly phoning home.

Even though I consider my network relatively clean, there were several dozens of open
connections all the time. Most of them go to the usual suspects (AWS, Google, Apple).
Some have surprised me — a direct connection to Moscow turned out to be a family member's
Yandex browser, and connections to Alibaba/ByteDance turned out to be my sister's TikTok.

## Technology

- [globe.gl](https://github.com/vasturiano/globe.gl)
- [MaxMind free Geo IP database](https://www.maxmind.com/en/geoip2-city-accuracy-comparison)

## Prerequisites

### Mikrotik

Prepare your router. Create a group with API and read-only access, then a user in that group:

```
/user group add name=mktvis policy=api,read
/user add name=mktvis group=mktvis password='top-secret'
```

### MaxMind account

Sign up for the [free MaxMind geolocation data](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en)
and generate a license key. The container downloads the databases on first start using this key.

## Docker

A container image is published to `ghcr.io` from every push to `main` and every git tag.

```bash
docker run -d \
  --name mktvis \
  --restart unless-stopped \
  -p 8080:80 \
  -e MKTVIS_ROUTERBOARD_ADDRESS=192.168.0.1 \
  -e MKTVIS_ROUTERBOARD_USER=mktvis \
  -e MKTVIS_ROUTERBOARD_PASSWORD='top-secret' \
  -e MKTVIS_ROUTERBOARD_PORT=8728 \
  -e MKTVIS_ROUTERBOARD_USE_SSL=false \
  -e MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_VERIFY=false \
  -e MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_PATH= \
  -e MKTVIS_CITY_DB_PATH=/var/opt/mktvis/GeoLite2-City.mmdb \
  -e MKTVIS_ASN_DB_PATH=/var/opt/mktvis/GeoLite2-ASN.mmdb \
  -e MKTVIS_HOME_LAT=54.3109861 \
  -e MKTVIS_HOME_LON=10.1296693 \
  -e MAXMIND_LICENSE_KEY='your-key' \
  ghcr.io/leonmortenrichter/mktvis:latest
```

Then open `http://localhost:8080` in your browser.

### Environment variables

| Variable | Type | Required | Notes |
|---|---|---|---|
| `MKTVIS_ROUTERBOARD_ADDRESS` | str | yes | IP/hostname of the Mikrotik device |
| `MKTVIS_ROUTERBOARD_USER` | str | yes | RouterOS API user |
| `MKTVIS_ROUTERBOARD_PASSWORD` | str | yes | RouterOS API password |
| `MKTVIS_ROUTERBOARD_PORT` | str | yes | RouterOS API port (usually `8728` or `8729` for SSL) |
| `MKTVIS_ROUTERBOARD_USE_SSL` | bool | yes | `1`/`true`/`yes`/`on` or `0`/`false`/`no`/`off` (case-insensitive) |
| `MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_VERIFY` | bool | yes | same bool syntax as above |
| `MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_PATH` | str | yes | path to CA bundle; empty string disables custom CA |
| `MKTVIS_HOME_LAT` | float | yes | latitude of your location (arc origin on the globe) |
| `MKTVIS_HOME_LON` | float | yes | longitude of your location |
| `MKTVIS_CITY_DB_PATH` | str | yes | path to `GeoLite2-City.mmdb` |
| `MKTVIS_ASN_DB_PATH` | str | yes | path to `GeoLite2-ASN.mmdb` |
| `MAXMIND_LICENSE_KEY` | str | no | downloads databases on first start when set |
| `MKTVIS_FORCE_DB_UPDATE` | str | no | set to `1` to re-download databases on every start |

### MaxMind databases

Two options:

1. Set `MAXMIND_LICENSE_KEY` and the entrypoint downloads them on first start.
2. Mount them as volumes at `MKTVIS_CITY_DB_PATH` / `MKTVIS_ASN_DB_PATH`.

### Network

The container shares the host network (`--network host`) so it can reach the Mikrotik
device on your LAN. Without host networking, the container's bridge network cannot route
to the router. If you must use a different network mode, ensure the Mikrotik IP is
reachable from the container.