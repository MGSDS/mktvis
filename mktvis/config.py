import os
import pathlib
import typing
import yaml

_ENV_PREFIX = 'MKTVIS_'

_BOOL_TRUE = frozenset({'1', 'true', 'yes', 'on'})
_BOOL_FALSE = frozenset({'0', 'false', 'no', 'off'})

_ENV_BOOL_KEYS = frozenset({
    'routerboard_use_ssl',
    'routerboard_ssl_certificate_verify',
})
_ENV_NULLABLE_STR_KEYS = frozenset({
    'routerboard_ssl_certificate_path',
    'maxmind_license_key',
})

_KEYS = (
    'routerboard_address',
    'routerboard_user',
    'routerboard_password',
    'routerboard_use_ssl',
    'routerboard_ssl_certificate_verify',
    'routerboard_ssl_certificate_path',
    'routerboard_port',
    'city_db_path',
    'asn_db_path',

)


class UnknownConfigurationKeyError(Exception):
    """Raised when the config loader encounters an unknown key"""

    def __init__(self, key: str) -> None:
        super().__init__(f'Unknown configuration key \'{key}\'')

        self.key = key


class MissingConfigurationKey(Exception):
    """Raised when the config has missing required keys"""

    def __init__(self, key: str) -> None:
        super().__init__(f'Missing configuration key \'{key}\'')

        self.key = key


class ConfigurationValueError(ValueError):
    """Raised when the configuration value is not atomic"""


def is_atomic(val: typing.Any) -> bool:
    if val is None:
        return True

    if isinstance(val, str):
        return True

    if isinstance(val, int):
        return True

    return False


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in _BOOL_TRUE:
        return True
    if lowered in _BOOL_FALSE:
        return False
    raise ConfigurationValueError(f'Cannot parse {value!r} as bool')


class MKTVISConfig:

    LISTEN_PORT: int

    ROUTERBOARD_ADDRESS: str
    ROUTERBOARD_PORT: str
    ROUTERBOARD_USER: str
    ROUTERBOARD_PASSWORD: str
    ROUTERBOARD_USE_SSL: str
    ROUTERBOARD_SSL_CERTIFICATE_VERIFY: str
    ROUTERBOARD_SSL_CERTIFICATE_PATH: str

    CITY_DB_PATH: str
    ASN_DB_PATH: str

    def __init__(self, key_value_dict: typing.Dict[str, typing.Any]) -> None:
        self._key_value_dict = key_value_dict

        missing = self.missing_keys
        if missing:
            raise MissingConfigurationKey(missing.pop())

    @property
    def missing_keys(self) -> typing.Set[str]:
        return set(_KEYS).difference(set(self._key_value_dict.keys()))

    def __str__(self) -> str:
        return str(self._key_value_dict)

    def __getattr__(self, __name: str) -> typing.Any:
        key = __name.lower()
        return self._key_value_dict[key]

    @classmethod
    def from_dict(cls, dict_obj: typing.Dict[str, typing.Any]) -> 'MKTVISConfig':
        key_value_dict = {k: None for k in _KEYS}
        for key, val in dict_obj.items():
            if key not in _KEYS:
                raise UnknownConfigurationKeyError(key)

            if not is_atomic(val):
                raise ConfigurationValueError(val)

            key_value_dict[key] = val

        return cls(key_value_dict)

    @classmethod
    def from_env(cls) -> 'MKTVISConfig':
        key_value_dict: typing.Dict[str, typing.Any] = {}
        for key in _KEYS:
            raw = os.environ.get(_ENV_PREFIX + key.upper())
            if raw is None:
                continue
            if key in _ENV_BOOL_KEYS:
                key_value_dict[key] = _parse_bool(raw)
            elif key in _ENV_NULLABLE_STR_KEYS:
                key_value_dict[key] = raw if raw != '' else None
            else:
                key_value_dict[key] = raw
        return cls(key_value_dict)

    @classmethod
    def load(cls, fpath: str) -> 'MKTVISConfig':
        path: pathlib.Path = pathlib.Path(fpath)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(
                f'{fpath} not found or not readable by application')

        with open(fpath, 'r') as fd:
            yaml_dict = yaml.safe_load(fd)
            return cls.from_dict(yaml_dict)
