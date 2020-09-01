import json as python_json
import logging

logger = logging.getLogger(__name__)


def write_json_file(abspath, data):
    json_path = abspath.with_suffix('.json')

    logger.info('write_json_file %s', json_path)

    with open(json_path, 'w') as f:
        f.write(python_json.dumps(data, indent=2))
