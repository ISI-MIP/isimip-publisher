import configparser
import json
import logging
import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

from .utils.fetch import (fetch_definitions, fetch_pattern, fetch_schema,
                          fetch_tree)

logger = logging.getLogger(__name__)


class Settings(object):

    _shared_state = {}

    CONFIG_FILES = [
        'isimip.conf',
        '~/.isimip.conf',
        '/etc/isimip.conf'
    ]

    DEFAULTS = {
        'LOG_LEVEL': 'WARN',
        'VERSION': date.today().strftime('%Y%m%d'),
        'PROTOCOL_LOCATIONS': 'https://protocol.isimip.org https://protocol2.isimip.org',
        'ISIMIP_DATA_URL': 'https://data.isimip.org/',
        'DATACITE_METADATA_URL': 'https://mds.datacite.org/metadata',
        'DATACITE_DOI_URL': 'https://mds.datacite.org/doi',
        'MOCK': 'false'
    }

    def __init__(self):
        self.__dict__ = self._shared_state

    def __str__(self):
        return str(vars(self))

    def setup(self, args):
        # setup env from .env file
        load_dotenv(Path().cwd() / '.env')

        # read config file
        config = self.read_config(args.config_file)

        # combine settings from args, os.environ, and config
        self.build_settings(args, os.environ, config)

        self.LOG_LEVEL = self.LOG_LEVEL.upper()
        self.LOG_FILE = Path(self.LOG_FILE).expanduser() if self.LOG_FILE else None
        self.MOCK = self.MOCK in [True, 1] or self.MOCK.lower() in ['true', 't', '1']

        if self.ISIMIP_DATA_URL is not None:
            self.ISIMIP_DATA_URL = self.ISIMIP_DATA_URL.rstrip('/')

        try:
            datetime.strptime(self.VERSION, '%Y%m%d')
        except ValueError:
            raise AssertionError("Incorrect version format, should be YYYYMMDD")

        # setup logs
        if self.LOG_FILE:
            logging.basicConfig(level=self.LOG_LEVEL, filename=self.LOG_FILE,
                                format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        else:
            logging.basicConfig(level=self.LOG_LEVEL,
                                format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')

        # log self
        logger.debug(self)

    def read_config(self, config_file_arg):
        config_files = [config_file_arg] + self.CONFIG_FILES
        for config_file in config_files:
            if config_file:
                config = configparser.ConfigParser()
                config.read(config_file)
                if 'isimip-publisher' in config:
                    return config['isimip-publisher']

    def build_settings(self, args, environ, config):
        args_dict = vars(args)
        for key, value in args_dict.items():
            if key not in ['func', 'config_file']:
                attr = key.upper()
                if value is not None:
                    attr_value = value
                elif environ.get(attr):
                    attr_value = environ.get(attr)
                elif config and config.get(key):
                    attr_value = config.get(key)
                else:
                    attr_value = self.DEFAULTS.get(attr)

                setattr(self, attr, attr_value)

    @property
    def REMOTE_PATH(self):
        assert self.REMOTE_DIR is not None, 'REMOTE_DIR is not set'
        return Path(self.REMOTE_DIR).expanduser()

    @property
    def LOCAL_PATH(self):
        assert self.LOCAL_DIR is not None, 'LOCAL_DIR is not set'
        return Path(self.LOCAL_DIR).expanduser()

    @property
    def PUBLIC_PATH(self):
        assert self.PUBLIC_DIR is not None, 'PUBLIC_DIR is not set'
        return Path(self.PUBLIC_DIR).expanduser()

    @property
    def ARCHIVE_PATH(self):
        assert self.ARCHIVE_DIR is not None, 'ARCHIVE_DIR is not set'
        return Path(self.ARCHIVE_DIR).expanduser()

    @property
    def EXCLUDE(self):
        if not hasattr(self, '_exclude'):
            self._exclude = self.parse_filelist(self.EXCLUDE_FILE)
        return self._exclude

    @property
    def INCLUDE(self):
        if not hasattr(self, '_include'):
            self._include = self.parse_filelist(self.INCLUDE_FILE)
        return self._include

    @property
    def RESOURCES(self):
        if not hasattr(self, '_resources'):
            self._resources = []
            for resource_json in self.RESOURCE_JSON:
                resource_path = Path(resource_json)
                self._resources.append(json.loads(resource_path.read_text()))

        return self._resources

    @property
    def DEFINITIONS(self):
        if not hasattr(self, '_definitions'):
            assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._definitions = fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PATH)

            assert self._definitions is not None, 'No definitions found for {}'.format(self.PATH)

        return self._definitions

    @property
    def PATTERN(self):
        if not hasattr(self, '_pattern'):
            assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._pattern = fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.PATH)

            assert self._pattern is not None, 'No pattern found for {}'.format(self.PATH)

        return self._pattern

    @property
    def SCHEMA(self):
        if not hasattr(self, '_schema'):
            assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._schema = fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.PATH)

            assert self._schema is not None, 'No schema found for {}'.format(self.PATH)

        return self._schema

    @property
    def TREE(self):
        if not hasattr(self, '_tree'):
            assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._tree = fetch_tree(self.PROTOCOL_LOCATIONS.split(), self.PATH)

            assert self._tree is not None, 'No tree for {}'.format(self.PATH)

        return self._tree

    def parse_filelist(self, filelist_file):
        if filelist_file:
            with open(filelist_file) as f:
                filelist = f.read().splitlines()
        else:
            filelist = None

        return filelist


class Store(object):

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.datasets = []


settings = Settings()
store = Store()
