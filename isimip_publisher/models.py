import logging
import mimetypes

import jsonschema

from .utils import order_dict
from .utils.checksum import (get_checksum, get_checksum_from_string,
                             get_checksum_type)
from .utils.config import (load_pattern, load_schema, parse_datacite,
                           parse_env, parse_filelist, parse_version)
from .utils.database import (insert_dataset, insert_file, publish_dataset,
                             unpublish_dataset)
from .utils.json import write_file_json
from .utils.thumbnails import write_thumbnail

logger = logging.getLogger(__name__)


class Store(object):

    def __init__(self, args):
        self.path = args.path

        for attr, value in parse_env().items():
            setattr(self, attr, value)

        self.version = parse_version(args.version)
        self.include = parse_filelist(args.include_file)
        self.exclude = parse_filelist(args.exclude_file)
        self.datacite = parse_datacite(args.datacite_file)

        self.pattern = load_pattern(self.path)
        self.schema = load_schema(self.path)

        self.datasets = []


class Dataset(object):

    def __init__(self, name, path, identifiers):
        self.name = name
        self.path = path
        self.identifiers = identifiers

        self.files = []
        self.checksum_type = get_checksum_type()
        self.clean = False

        self._checksum = None

    @property
    def checksum(self):
        if not self._checksum:
            self._checksum = get_checksum_from_string(''.join([file.checksum for file in self.files]))
        return self._checksum

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            try:
                jsonschema.validate(schema=schema, instance=self.identifiers)
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('identifiers = %s', self.identifiers)
                raise e

    def check(self, db_file):
        logger.info('path = %s, checksum = %s', self.path, self.checksum)
        assert str(self.path) == db_file.path, (str(self.path), db_file.path)
        assert self.checksum == db_file.checksum, (self.checksum, db_file.checksum)

    def insert(self, session, version):
        insert_dataset(session, version, self.name, self.path, self.checksum, self.checksum_type, self.identifiers)

    def publish(self, session, version):
        publish_dataset(session, version, self.path)

    def unpublish(self, session):
        return unpublish_dataset(session, self.path)


class File(object):

    def __init__(self, dataset, name, path, abspath, identifiers):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.abspath = abspath
        self.identifiers = identifiers

        self.mime_type = str(mimetypes.guess_type(str(self.abspath))[0])
        self.checksum_type = get_checksum_type()
        self.clean = False

        self._checksum = None

    @property
    def checksum(self):
        if not self._checksum:
            self._checksum = get_checksum(self.abspath)
        return self._checksum

    def validate(self, schema):
        # validate if self.clean is not true yet
        if self.clean:
            return self.clean
        else:
            try:
                jsonschema.validate(schema=schema, instance=self.identifiers)
                self.clean = True
            except jsonschema.exceptions.ValidationError as e:
                logger.error('identifiers = %s', self.identifiers)
                raise e

    def check(self, db_file):
        logger.info('path = %s, checksum = %s', self.path, self.checksum)
        assert str(self.path) == db_file.path, (str(self.path), db_file.path)
        assert self.checksum == db_file.checksum, (self.checksum, db_file.checksum)

    def write_json(self):
        attributes = {
            'path': str(self.path),
            'checksum':  self.checksum,
            'checksum_type':  self.checksum_type
        }
        attributes.update(self.identifiers)

        write_file_json(self.abspath, order_dict(attributes))

    def write_thumbnail(self, mock=False):
        write_thumbnail(self.abspath, mock=False)

    def insert(self, session, version):
        insert_file(session, version, self.dataset.path, self.name, self.path,
                    self.mime_type, self.checksum, self.checksum_type, self.identifiers)
