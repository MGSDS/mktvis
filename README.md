# Live plot open connections from your Mikrotik device on a 3-dimensional globe

A straightforward Python module to export and visualize open connections from any
Mikrotik RouterOS device. It gathers open connections through the RouterOS REST API,
enriches them with geolocation data and visualizes the result on an interactive 3D globe.

![example image](./img/screen.png)

## Disclaimer

This project was born out of pure boredom and the urge to play around with
[globe.gl](https://github.com/vasturiano/globe.gl).
IP geolocation data is inherently inaccurate and should be considered a rough guess.
This displayed data does not provide any security gain. On the contrary, since the data
is retrieved via the RouterOS API, it is extremely important to take appropriate
precautions to not compromise the integrity of your router:

- use HTTPS instead of HTTP
- choose a secure password
- secure the device on which the service is running

## What is the purpose ?

One can argue that the added value of this project is limited. Ultimately, this is only a (pretty) visualization of one's IP connections.

But the visualization can be used vividly demonstrate how interconnected modern devices are today. 
In my family, which does not have a particular affinity for technology, I was able to generate some amazement.
Evidently, not everyone was aware that our smart helpers are constantly phoning home.

Even though I consider my network relatively clean, there were several dozens of open connections all the time.
Most of them go to the usual suspects:

- AWS
- Google / Google Cloud
- Apple services

Some connections, on the other hand, have surprised me. For example, I was surprised by a connection that went directly to Moscow.
After a short investigation, it turned out that it was the device of a family member. The user is an avid user of the Yandex 
browser and the associated mail service. His device was permanently connected to the corresponding Yandex services. 

![spotted connection to Yandex](./img/yandex.png)

In addition, I wondered about a connection to Alibaba and ByteDance, which was also constantly open. Since I'm meticulous
about making sure all IoT devices are on their own offline VLAN, I wondered if I had missed something.
However, it turned out that these connections were coming from my little sister's smartphone. She has TikTok installed on the device.

![spotted connection to ByteDance](./img/bytedance.png)

So you can definitely get some insights into your own home network.

## Technology used

- [globe.gl](https://github.com/vasturiano/globe.gl)
- [MaxMind free Geo IP database](https://www.maxmind.com/en/geoip2-city-accuracy-comparison)

## Installation

### Mikrotik

At first you need to prepare your router.

Create a group on the device that has API and read-only access:

`/user group add name=mktvis policy=api,read`

Create a user that is part of the group:

`/user add name=mktvis group=mktvis password='top-secret'

### MaxMind free Account

You need an free account for the MaxMin [free geolocation data](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en).
Once you signed up, you need to generate a license key. This key will be used to download the required database(s).

### Prepare a Raspi (or any other machine)

I deployed this service to a Raspberry Pi. Therefore, I created a simple Ansible Playbook.
If you prefer Docker, see the [Docker](#docker) section below. Otherwise, prepare a physical
or virtual machine that you have SSH access to.

### Prepare the Playbook

Adapt `setup/install.yml` to your needs:

```yaml
    home:
      # Defaults to Kiel, Germany - not my actual home address
      # Change this to your coordinates
      lat: 54.3109861
      lon: 10.1296693

    routerboard_address: '192.168.0.1'              # This is your Mikrotik device to monitor
    routerboard_user: 'mktvis'                      # This is user used to authenticate against the Mikrotik API
    routerboard_password: 'top-secret'              # This is password used to authenticate against the Mikrotik API
    routerboard_use_ssl: false                      # Set to true to enable SSL encryption (encouraged)
    routerboard_ssl_certificate_verify: false       # Set to true to enable SSL certificate verification (encouraged)

    maxmind_license_key: '1234'                     # Replace with your MaxMind license key
```
Finally, run the Playbook:

```bash
pip install -U ansible
ansible-galaxy install geerlingguy.nginx
ansible-playbook setup/install.yml -i 192.168.0.11,
```

## Docker

A container image is published to `ghcr.io` from every push to `main` and every git tag.

```bash
docker run -d \
  --name mktvis \
  --restart unless-stopped \
  -p 127.0.0.1:5555:5555 \
  -e MKTVIS_ROUTERBOARD_ADDRESS=192.168.0.1 \
  -e MKTVIS_ROUTERBOARD_USER=mktvis \
  -e MKTVIS_ROUTERBOARD_PASSWORD='top-secret' \
  -e MKTVIS_ROUTERBOARD_PORT=8728 \
  -e MKTVIS_ROUTERBOARD_USE_SSL=false \
  -e MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_VERIFY=false \
  -e MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_PATH= \
  -e MKTVIS_LISTEN_PORT=5555 \
  -e MKTVIS_CITY_DB_PATH=/var/opt/mktvis/GeoLite2-City.mmdb \
  -e MKTVIS_ASN_DB_PATH=/var/opt/mktvis/GeoLite2-ASN.mmdb \
  -e MAXMIND_LICENSE_KEY='your-key' \
  ghcr.io/leonmortenrichter/mktvis:latest
```

The image is configured exclusively via environment variables. No config file is required or read.

### Environment variables

All variables are prefixed with `MKTVIS_` and map 1:1 to the YAML keys used by the
Ansible deployment.

| Variable | Type | Required | Notes |
|---|---|---|---|
| `MKTVIS_ROUTERBOARD_ADDRESS` | str | yes | IP/hostname of the Mikrotik device |
| `MKTVIS_ROUTERBOARD_USER` | str | yes | RouterOS API user |
| `MKTVIS_ROUTERBOARD_PASSWORD` | str | yes | RouterOS API password |
| `MKTVIS_ROUTERBOARD_PORT` | str | yes | RouterOS API port (usually `8728` or `8729` for SSL) |
| `MKTVIS_ROUTERBOARD_USE_SSL` | bool | yes | `1`/`true`/`yes`/`on` or `0`/`false`/`no`/`off` (case-insensitive) |
| `MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_VERIFY` | bool | yes | same bool syntax as above |
| `MKTVIS_ROUTERBOARD_SSL_CERTIFICATE_PATH` | str | yes | path to CA bundle; empty string disables custom CA |
| `MKTVIS_LISTEN_PORT` | str | yes | port the HTTP exporter binds to |
| `MKTVIS_CITY_DB_PATH` | str | yes | path to `GeoLite2-City.mmdb` |
| `MKTVIS_ASN_DB_PATH` | str | yes | path to `GeoLite2-ASN.mmdb` |
| `MKTVIS_MAXMIND_LICENSE_KEY` | str | no | when set, the entrypoint downloads the databases on first start |
| `MAXMIND_LICENSE_KEY` | str | no | alias used by the entrypoint download script (set one or the other) |

The MaxMind databases can be provided in two ways:

1. Let the entrypoint download them on first start by setting `MAXMIND_LICENSE_KEY`.
2. Mount them as volumes at the paths given by `MKTVIS_CITY_DB_PATH` / `MKTVIS_ASN_DB_PATH`.
