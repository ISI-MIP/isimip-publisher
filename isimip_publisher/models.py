from functools import cached_property
import json
import logging
from pathlib import Path

import jsonschema

from isimip_utils.checksum import get_checksum, get_checksum_type
from isimip_utils.netcdf import (open_dataset_read, get_dimensions,
                                 get_global_attributes, get_variables)

from .utils.files import get_size

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

    @cached_property
    def size(self):
        return sum([file.size for file in self.files])

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

    @cached_property
    def uuid(self):
        return self.netcdf_header.get('global_attributes', {}).get('isimip_id')

    @cached_property
    def netcdf_header(self):
        if Path(self.path).suffix.startswith('.nc'):
            with open_dataset_read(self.abspath) as dataset:
                return {
                    'dimensions': get_dimensions(dataset),
                    'variables': get_variables(dataset, convert=True),
                    'global_attributes': get_global_attributes(dataset, convert=True)
                }

    @cached_property
    def size(self):
        return get_size(self.abspath)

    @cached_property
    def checksum(self):
        json_file = Path(self.abspath).with_suffix('.json')
        if json_file.is_file():
            return json.loads(json_file.read_text()).get('checksum')
        else:
            return get_checksum(self.abspath, self.checksum_type)

    @cached_property
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
