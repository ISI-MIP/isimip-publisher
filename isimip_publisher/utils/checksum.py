import hashlib
import os


def get_checksum(file):
    m = hashlib.sha256()

    with open(file, 'rb') as f:
        # read and update in blocks of 4K
        for block in iter(lambda: f.read(4096), b''):
            m.update(block)

    return m.hexdigest()


def write_checksum(file):
    with open(file.replace('.nc4', '.sha256'), 'w') as f:
        f.write(get_checksum(file) + '  ' + os.path.basename(file) + os.linesep)
