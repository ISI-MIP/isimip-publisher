import json
import logging
import os
import re
from urllib.parse import urlparse

import requests
from jsonschema import RefResolver

logger = logging.getLogger(__name__)


def fetch_pattern(schema_path):
    pattern_base = os.getenv('PATTERN_LOCATION', 'http://schema.isimip.org/pattern/')
    pattern_location = pattern_base + schema_path

    if urlparse(pattern_location).scheme:
        logger.debug('pattern_url = %s', pattern_location)
        response = requests.get(pattern_location)
        response.raise_for_status()
        pattern_json = response.json()
    else:
        logger.debug('pattern_path = %s', pattern_location)
        pattern_json = json.loads(open(pattern_location).read())

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
    schema_base = os.getenv('SCHEMA_LOCATION', 'http://schema.isimip.org/pattern/')
    schema_location = schema_base + schema_path

    if urlparse(schema_location).scheme:
        logger.debug('schema_url = %s', schema_location)
        schema_response = requests.get(schema_location)
        schema_response.raise_for_status()
        return schema_response.json()
    else:
        logger.debug('schema_path = %s', schema_location)
        schema = json.loads(open(schema_location).read())

        # remove $id to make it work locally
        schema.pop('$id')
        return schema


def get_resolver(schema_path, schema):
    schema_base = os.getenv('SCHEMA_LOCATION', 'http://schema.isimip.org/pattern/')
    schema_location = schema_base + schema_path

    if urlparse(schema_location).scheme:
        return None
    else:
        dirname = os.path.abspath(schema_location)
        base_uri = 'file://{}'.format(dirname)
        logger.debug('base_uri = %s', base_uri)
        return RefResolver(base_uri, None)
