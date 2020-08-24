import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def fetch_pattern(pattern_locations, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        pattern_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')
        pattern_json = fetch_json(pattern_locations, pattern_path)

        if pattern_json:
            logger.info('pattern_path = %s', pattern_path)
            logger.debug('pattern_json = %s', pattern_json)

            assert isinstance(pattern_json['path'], str)
            assert isinstance(pattern_json['file'], str)
            assert isinstance(pattern_json['dataset'], str)
            assert isinstance(pattern_json['suffix'], list)

            pattern = {
                'path': re.compile(pattern_json['path']),
                'file': re.compile(pattern_json['file']),
                'dataset': re.compile(pattern_json['dataset']),
                'suffix': pattern_json['suffix']
            }

            logger.debug('pattern = %s', pattern)

            return pattern


def fetch_schema(schema_locations, path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        schema_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')
        schema_json = fetch_json(schema_locations, schema_path)

        if schema_json:
            logger.info('schema_path = %s', schema_path)
            logger.debug('schema_json = %s', schema_json)
            return schema_json


def fetch_json(bases, path):
    for base in bases:
        if urlparse(base).scheme:
            location = base.rstrip('/') + path.as_posix()
            logger.debug('json_url = %s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base) / path
            logger.debug('json_path = %s', location)

            if location.exists():
                return json.loads(open(location).read())
