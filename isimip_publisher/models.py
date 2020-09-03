import json
import logging
import mimetypes
from datetime import datetime
from pathlib import Path

import jsonschema

from .config import settings
from .utils.checksum import (get_checksum, get_checksum_type,
                             get_checksums_checksum)
from .utils.fetch import fetch_pattern, fetch_schema
from .utils.netcdf import get_netcdf_global_attributes

logger = logging.getLogger(__name__)


class Store(object):

    def __init__(self, path):
        self.path = path
        self.datasets = []

    @property
    def remote_dest(self):
        assert settings.REMOTE_DEST is not None, 'REMOTE_DEST is not set'
        return settings.REMOTE_DEST

    @property
    def remote_path(self):
        assert settings.REMOTE_DIR is not None, 'REMOTE_DIR is not set'
        return Path(settings.REMOTE_DIR).expanduser()

    @property
    def local_path(self):
        assert settings.LOCAL_DIR is not None, 'LOCAL_DIR is not set'
        return Path(settings.LOCAL_DIR).expanduser()

    @property
    def public_path(self):
        assert settings.PUBLIC_DIR is not None, 'PUBLIC_DIR is not set'
        return Path(settings.PUBLIC_DIR).expanduser()

    @property
    def archive_path(self):
        assert settings.ARCHIVE_DIR is not None, 'ARCHIVE_DIR is not set'
        return Path(settings.ARCHIVE_DIR).expanduser()

    @property
    def database(self):
        assert settings.DATABASE is not None, 'DATABASE is not set'
        return settings.DATABASE

    @property
    def isimip_data_url(self):
        assert settings.ISIMIP_DATA_URL is not None, 'ISIMIP_DATA_URL is not set'
        return settings.ISIMIP_DATA_URL.rstrip('/')

    @property
    def version(self):
        if not hasattr(self, '_version'):
            try:
                datetime.strptime(settings.VERSION, '%Y%m%d')
                self._version = settings.VERSION
            except ValueError:
                raise AssertionError("Incorrect version format, should be YYYYMMDD")

        return self._version

    @property
    def exclude(self):
        if not hasattr(self, '_exclude'):
            self._exclude = self.parse_filelist(settings.EXCLUDE_FILE)
        return self._exclude

    @property
    def include(self):
        if not hasattr(self, '_include'):
            self._include = self.parse_filelist(settings.INCLUDE_FILE)
        return self._include

    @property
    def datacite(self):
        if not hasattr(self, '_datacite'):
            assert settings.DATACITE_FILE is not None, 'DATACITE_FILE is not set'

            with open(settings.DATACITE_FILE) as f:
                self._datacite = json.loads(f.read())

        return self._datacite

    @property
    def pattern(self):
        if not hasattr(self, '_pattern'):
            assert settings.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._pattern = fetch_pattern(settings.PROTOCOL_LOCATIONS.split(), self.path)

            assert self._pattern is not None, 'No pattern found for {}'.format(self.path)

        return self._pattern

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            assert settings.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'

            self._schema = fetch_schema(settings.PROTOCOL_LOCATIONS.split(), self.path)

            assert self._schema is not None, 'No schema found for {}'.format(self.path)

        return self._schema

    def parse_filelist(self, filelist_file):
        if filelist_file:
            with open(filelist_file) as f:
                filelist = f.read().splitlines()
        else:
            filelist = None

        return filelist


class Dataset(object):

    def __init__(self, name=None, path=None, specifiers=None):
        self.name = name
        self.path = path
        self.specifiers = specifiers
        self.files = []
        self.checksum_type = get_checksum_type()
        self.clean = False

        self._checksum = None

    @property
    def checksum(self):
        if not self._checksum:
            self._checksum = get_checksums_checksum([file.checksum for file in self.files], self.checksum_type)
        return self._checksum

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            try:
                jsonschema.validate(schema=schema, instance={
                    'specifiers': dict(self.specifiers)
                })
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('instance = %s', self.json)
                raise e


class File(object):

    def __init__(self, dataset=None, name=None, path=None, abspath=None, specifiers=None):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.abspath = abspath
        self.specifiers = specifiers
        self.mime_type = str(mimetypes.guess_type(str(self.abspath))[0])
        self.checksum_type = get_checksum_type()
        self.clean = False

        self._uuid = None
        self._checksum = None

    @property
    def uuid(self):
        if not self._uuid:
            self._uuid = get_netcdf_global_attributes(self.abspath).get('isimip_id')
        return self._uuid

    @property
    def checksum(self):
        if not self._checksum:
            self._checksum = get_checksum(self.abspath, self.checksum_type)
        return self._checksum

    @property
    def json(self):
        return {
            'id': self._uuid,
            'path': str(self.path),
            'checksum':  self.checksum,
            'checksum_type':  self.checksum_type,
            'specifiers': dict(self.specifiers)
        }

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            try:
                jsonschema.validate(schema=schema, instance={
                    'specifiers': dict(self.specifiers)
                })
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('instance = %s', self.json)
                raise e
