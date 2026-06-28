import os

from mktvis.collector import COLLECTOR
from mktvis.config import ConfigurationValueError, MKTVISConfig
from mktvis.connection import MaxMindDatabaseConnection, RouterConnection
from mktvis.server import ExportProcessor


def main() -> None:
    # Create and init all instances that need to access the config
    # The actual instances are decoupled from the config object
    # Therefore, these need to be instantiated individually
    source = os.environ.get('MKTVIS_CONFIG_SOURCE', 'file')
    if source == 'env':
        config = MKTVISConfig.from_env()
    elif source == 'file':
        config = MKTVISConfig.load(os.environ.get('MKTVIS_CONFIG', '/etc/mktvis/config.yml'))
    else:
        raise ConfigurationValueError(f'Unknown MKTVIS_CONFIG_SOURCE={source!r}')

    with RouterConnection.from_config(config) as router_conn, MaxMindDatabaseConnection.from_config(config) as maxmind_conn:
        COLLECTOR.init(router_conn, maxmind_conn)  # type:ignore

        # This start the server which collects connection data on demand
        ExportProcessor.run(port=int(config.LISTEN_PORT))


if __name__ == '__main__':
    main()
