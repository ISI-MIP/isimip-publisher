import hashlib
import os
from pathlib import Path


def get_checksum(file_abspath):
    m = hashlib.sha256()

    with open(file_abspath, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)

    return m.hexdigest()


def get_checksum_type():
    return 'sha256'


def write_checksum(file):
    checksum_path = file['abspath'].with_suffix('.sha256')
    checksum = get_checksum(file['abspath'])

    with open(checksum_path, 'w') as f:
        f.write(checksum + os.linesep)
