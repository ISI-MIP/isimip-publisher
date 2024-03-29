import logging
from datetime import datetime
from pathlib import Path

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import fetch_definitions, fetch_pattern, fetch_resource, fetch_schema, fetch_tree
from isimip_utils.utils import parse_filelist

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

    def setup(self, args):
        super().setup(args)

        if self.ISIMIP_DATA_URL is not None:
            self.ISIMIP_DATA_URL = self.ISIMIP_DATA_URL.rstrip('/')

        if self.RIGHTS not in RIGHTS_CHOICES:
            raise RuntimeError('Incorrect rights "%s": choose from %s', self.RIGHTS, RIGHTS_CHOICES)

        try:
            datetime.strptime(self.VERSION, '%Y%m%d')
        except ValueError as e:
            raise RuntimeError('Incorrect version format, should be YYYYMMDD') from e

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
    def ARCHIVE_PATH(self):
        if self.ARCHIVE_DIR is None:
            raise RuntimeError('ARCHIVE_DIR is not set')
        return Path(self.ARCHIVE_DIR).expanduser()

    @cached_property
    def EXCLUDE(self):
        return parse_filelist(self.EXCLUDE_FILE)

    @cached_property
    def INCLUDE(self):
        return parse_filelist(self.INCLUDE_FILE)

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
            raise RuntimeError('RESOURCE_LOCATION is not set')
        return fetch_resource(self.RESOURCE_LOCATION)

    @cached_property
    def DEFINITIONS(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def PATTERN(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def SCHEMA(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def TREE(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_tree(self.PROTOCOL_LOCATIONS.split(), self.PATH)


class Store:

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.datasets = []


settings = Settings()
store = Store()
