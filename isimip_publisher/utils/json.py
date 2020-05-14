import json as python_json
import logging

from .checksum import get_checksum_type, get_file_checksum

logger = logging.getLogger(__name__)


def write_file_json(config, file, attributes):
    json_path = file['abspath'].with_suffix('.json')

    logger.info('write_file_json %s', json_path)

    attributes.update({
        'path': str(file['path']),
        'checksum':  get_file_checksum(file),
        'checksum_type':  get_checksum_type()
    })

    with open(json_path, 'w') as f:
        f.write(python_json.dumps(attributes, indent=2))
