import hashlib
import logging

logger = logging.getLogger(__name__)


def get_checksum_from_string(string):
    m = hashlib.sha1()
    m.update(string.encode())
    return m.hexdigest()


def get_checksum(abspath):
    m = hashlib.sha1()

    with open(abspath, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)

    return m.hexdigest()


def get_checksum_type():
    return 'sha1'
