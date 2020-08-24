import configparser
import logging
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

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
        'PATTERN_LOCATIONS': 'https://protocol.isimip.org/pattern/',
        'SCHEMA_LOCATIONS': 'https://protocol.isimip.org/pattern/',
        'ISIMIP_DATA_URL': 'https://data.isimip.org/'
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

        # setup logs
        if self.LOG_FILE:
            logging.basicConfig(level=self.LOG_LEVEL, filename=self.LOG_FILE,
                                format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        else:
            logging.basicConfig(level=self.LOG_LEVEL,
                                format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')

        # log settings
        logger.debug(self)

    def print(self):
        for key, value in vars(self).items():
            if key not in ['DATABASE']:
                print('%s = %s' % (key, value))

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
            if key not in ['func', 'path', 'config_file']:
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


settings = Settings()
