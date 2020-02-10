import json
import logging
import os
import re
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def fetch_pattern(pattern_path):
    pattern_bases = os.environ['PATTERN_LOCATIONS'].split()
    pattern_json = fetch_json(pattern_bases, pattern_path)
    logger.debug('pattern_json = %s', pattern_json)

    path_pattern = os.sep.join(pattern_json['path']) + '$'
    file_pattern = '^' + '_'.join(pattern_json['file']) + '.nc4'
    dataset_pattern = '^' + '_'.join(pattern_json['dataset'])

    pattern = {
        'path': re.compile(path_pattern),
        'file': re.compile(file_pattern),
        'dataset': re.compile(dataset_pattern)
    }

    logger.debug('pattern = %s', pattern['path'])

    return pattern


def fetch_schema(schema_path):
    schema_bases = os.environ['SCHEMA_LOCATIONS'].split()
    schema_json = fetch_json(schema_bases, schema_path)
    logger.debug('schema_json = %s', schema_json)

    return schema_json


def fetch_json(bases, path):
    for base in bases:
        location = os.path.join(base, path)

        if urlparse(location).scheme:
            logger.debug('json_url = %s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            logger.debug('json_path = %s', location)

            if os.path.exists(location):
                return json.loads(open(location).read())

    raise RuntimeError('{} not found in {}'.format(path, bases))
