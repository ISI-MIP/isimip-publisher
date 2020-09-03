import hashlib
import logging

logger = logging.getLogger(__name__)


CHECKSUM_TYPE = 'sha512'


def get_checksums_checksum(checksums, checksum_type=CHECKSUM_TYPE):
    m = hashlib.new(checksum_type)
    for checksum in checksums:
        m.update(checksum.encode())
    return m.hexdigest()


def get_checksum(abspath, checksum_type=CHECKSUM_TYPE):
    m = hashlib.new(checksum_type)
    with open(abspath, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)
    return m.hexdigest()


def get_checksum_type():
    return CHECKSUM_TYPE
