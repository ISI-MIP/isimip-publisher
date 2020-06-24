import mimetypes

from .utils import order_dict
from .utils.checksum import (get_checksum, get_checksum_from_string,
                             get_checksum_type)
from .utils.config import (load_pattern, load_schema, parse_filelist,
                           parse_version)
from .utils.database import (insert_dataset, insert_file, publish_dataset,
                             unpublish_dataset)
from .utils.json import write_file_json
from .utils.thumbnails import write_thumbnail
from .utils.validation import validate_identifiers


class Store(object):

    def __init__(self, args):
        self.path = args.path
        self.version = parse_version(args.version)
        self.filelist = parse_filelist(args.filelist_file)

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
        return self.clean or validate_identifiers(schema, self.identifiers)

    def insert(self, session, version):
        insert_dataset(session, version, self.name, self.path, self.checksum, self.checksum_type, self.identifiers)

    def publish(self, session, version):
        publish_dataset(session, version, self.path)

    def unpublish(self, session):
        unpublish_dataset(session, self.path)


class File(object):

    def __init__(self, dataset, name, path, abspath, identifiers):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.abspath = abspath
        self.identifiers = identifiers

        self.mime_type = str(mimetypes.guess_type(self.abspath)[0])
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
        return self.clean or validate_identifiers(schema, self.identifiers)

    def write_json(self):
        attributes = {
            'path': str(self.path),
            'checksum':  self.checksum,
            'checksum_type':  self.checksum_type
        }
        attributes.update(self.identifiers)

        write_file_json(self.abspath, order_dict(attributes))

    def write_thumbnail(self):
        write_thumbnail(self.abspath)

    def insert(self, session, version):
        insert_file(session, version, self.dataset.path, self.name, self.path,
                    self.mime_type, self.checksum, self.checksum_type, self.identifiers)
