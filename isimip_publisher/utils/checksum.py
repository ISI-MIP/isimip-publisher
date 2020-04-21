import hashlib
import logging

logger = logging.getLogger(__name__)


def get_dataset_checksum(dataset):
    m = hashlib.sha1()

    for file in dataset['files']:
        m.update(get_checksum(file['abspath']).encode())

    return m.hexdigest()


def get_file_checksum(file):
    return get_checksum(file['abspath'])


def get_checksum(file_abspath):
    m = hashlib.sha1()

    with open(file_abspath, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)

    return m.hexdigest()


def get_checksum_type():
    return 'sha1'
