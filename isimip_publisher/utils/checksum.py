import hashlib
import os


def get_checksum(file_abspath):
    m = hashlib.sha256()

    with open(file_abspath, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)

    return m.hexdigest()


def get_checksum_type():
    return 'sha256'


def write_checksum(file_abspath):
    with open(file_abspath.replace('.nc4', '.sha256'), 'w') as f:
        f.write(get_checksum(file_abspath) + os.linesep)
