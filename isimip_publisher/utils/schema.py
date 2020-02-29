import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def fetch_pattern(pattern_path):
    pattern_bases = os.environ['PATTERN_LOCATIONS'].split()
    pattern_json = fetch_json(pattern_bases, pattern_path)
    logger.debug('pattern_json = %s', pattern_json)

    pattern = {
        'path': re.compile(pattern_json['path']),
        'file': re.compile(pattern_json['file']),
        'dataset': re.compile(pattern_json['dataset'])
    }

    logger.debug('pattern = %s', pattern)

    return pattern


def fetch_schema(schema_path):
    schema_bases = os.environ['SCHEMA_LOCATIONS'].split()
    schema_json = fetch_json(schema_bases, schema_path)
    logger.debug('schema_json = %s', schema_json)

    return schema_json


def fetch_json(bases, path):
    for base in bases:
        if urlparse(base).scheme:
            location = base + path
            logger.debug('json_url = %s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base) / path
            logger.debug('json_path = %s', location)

            if location.exists():
                return json.loads(open(location).read())

    raise RuntimeError('{} not found in {}'.format(path, bases))
