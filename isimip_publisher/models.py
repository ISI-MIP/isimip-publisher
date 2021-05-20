import json
import logging
from pathlib import Path

import jsonschema

from .utils.checksum import get_checksum, get_checksum_type
from .utils.files import get_size
from .utils.netcdf import (get_netcdf_dimensions, get_netcdf_global_attributes,
                           get_netcdf_variables)

logger = logging.getLogger(__name__)


class Dataset(object):

    def __init__(self, name=None, path=None, specifiers=None):
        self.name = name
        self.path = path
        self.specifiers = specifiers
        self.files = []
        self.exclude = False
        self.clean = False

        self._size = None
        self._checksum = None

    @property
    def size(self):
        if not self._size:
            self._size = sum([file.size for file in self.files])
        return self._size

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            instance = {
                'specifiers': dict(self.specifiers)
            }
            try:
                jsonschema.validate(schema=schema, instance=instance)
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('instance = %s', instance)
                raise e


class File(object):

    def __init__(self, dataset=None, name=None, path=None, abspath=None, specifiers=None):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.abspath = abspath
        self.specifiers = specifiers
        self.checksum_type = get_checksum_type()
        self.clean = False

        self._uuid = None
        self._size = None
        self._checksum = None
        self._netcdf_header = None

    @property
    def uuid(self):
        if not self._uuid and self.netcdf_header:
            self._uuid = self.netcdf_header.get('global_attributes', {}).get('isimip_id')
        return self._uuid

    @property
    def netcdf_header(self):
        if not self._netcdf_header and Path(self.path).suffix.startswith('.nc'):
            self._netcdf_header = {
                'dimensions': get_netcdf_dimensions(self.abspath),
                'variables': get_netcdf_variables(self.abspath),
                'global_attributes': get_netcdf_global_attributes(self.abspath)
            }
        return self._netcdf_header

    @property
    def size(self):
        if not self._size:
            self._size = get_size(self.abspath)
        return self._size

    @property
    def checksum(self):
        if not self._checksum:
            json_file = Path(self.abspath).with_suffix('.json')
            if json_file.is_file():
                self._checksum = json.loads(json_file.read_text()).get('checksum')
            else:
                self._checksum = get_checksum(self.abspath, self.checksum_type)
        return self._checksum

    @property
    def json(self):
        return {
            'id': self._uuid,
            'path': self.path,
            'size': self.size,
            'checksum': self.checksum,
            'checksum_type': self.checksum_type,
            'specifiers': dict(self.specifiers),
            'netcdf_header': self.netcdf_header
        }

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            instance = {
                'specifiers': dict(self.specifiers)
            }
            try:
                jsonschema.validate(schema=schema, instance=instance)
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('instance = %s', instance)
                raise e
