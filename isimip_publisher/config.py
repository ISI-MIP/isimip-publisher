import logging
from functools import cached_property
from pathlib import Path
from urllib.parse import urlparse

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.config import Singleton
from isimip_utils.exceptions import ConfigError
from isimip_utils.fetch import fetch_json, load_json
from isimip_utils.protocol import fetch_definitions, fetch_pattern, fetch_schema, fetch_tree

logger = logging.getLogger(__name__)

RIGHTS_CHOICES = [
    None,
    'CC0',
    'BY',
    'BY-SA',
    'BY-NC',
    'BY-NC-SA'
]

class Settings(BaseSettings):

    @cached_property
    def REMOTE_PATH(self):
        if self.REMOTE_DIR is None:
            raise RuntimeError('REMOTE_DIR is not set')
        return Path(self.REMOTE_DIR).expanduser()

    @cached_property
    def LOCAL_PATH(self):
        if self.LOCAL_DIR is None:
            raise RuntimeError('LOCAL_DIR is not set')
        return Path(self.LOCAL_DIR).expanduser()

    @cached_property
    def PUBLIC_PATH(self):
        if self.PUBLIC_DIR is None:
            raise RuntimeError('PUBLIC_DIR is not set')
        return Path(self.PUBLIC_DIR).expanduser()

    @cached_property
    def RESTRICTED_PATH(self):
        if self.RESTRICTED_DIR is None:
            raise RuntimeError('RESTRICTED_DIR is not set')
        return Path(self.RESTRICTED_DIR).expanduser()

    @cached_property
    def ARCHIVE_PATH(self):
        if self.ARCHIVE_DIR is None:
            raise ConfigError('ARCHIVE_DIR is not set')
        return Path(self.ARCHIVE_DIR).expanduser()

    @cached_property
    def TARGET_EXCLUDE(self):
        return [
            file.replace(self.PATH, self.TARGET_PATH) for file in self.EXCLUDE
        ] if self.EXCLUDE else None

    @cached_property
    def TARGET_INCLUDE(self):
        return [
            file.replace(self.PATH, self.TARGET_PATH) for file in self.INCLUDE
        ] if self.INCLUDE else None

    @cached_property
    def RESOURCE(self):
        if self.RESOURCE_LOCATION is None:
            raise ConfigError('RESOURCE_LOCATION is not set')

        if not isinstance(self.RESOURCE_LOCATION, Path) and urlparse(self.RESOURCE_LOCATION).scheme:
            resource = fetch_json(self.RESOURCE_LOCATION)
        else:
            resource = load_json(self.RESOURCE_LOCATION)

        if resource is None:
            raise ConfigError(f'No resource found at {settings.RESOURCE_LOCATION}.')

        return resource

    @cached_property
    def DEFINITIONS(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise ConfigError('PROTOCOL_LOCATIONS is not set')
        return fetch_definitions(self.PATH, self.PROTOCOL_LOCATIONS)

    @cached_property
    def PATTERN(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise ConfigError('PROTOCOL_LOCATIONS is not set')
        return fetch_pattern(self.PATH, self.PROTOCOL_LOCATIONS)

    @cached_property
    def SCHEMA(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise ConfigError('PROTOCOL_LOCATIONS is not set')
        return fetch_schema(self.PATH, self.PROTOCOL_LOCATIONS)

    @cached_property
    def TREE(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise ConfigError('PROTOCOL_LOCATIONS is not set')
        return fetch_tree(self.PATH, self.PROTOCOL_LOCATIONS)


class Store(Singleton):
    datasets = []


settings = Settings()
store = Store()
