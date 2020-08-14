import json as python_json
import logging

logger = logging.getLogger(__name__)


def write_file_json(abspath, data):
    json_path = abspath.with_suffix('.json')

    logger.info('write_file_json %s', json_path)

    with open(json_path, 'w') as f:
        f.write(python_json.dumps(data, indent=2))
