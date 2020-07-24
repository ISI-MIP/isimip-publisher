import hashlib
import logging

logger = logging.getLogger(__name__)


def get_checksums_checksum(checksums):
    m = hashlib.sha1()
    for checksum in checksums:
        m.update(checksum.encode())
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
