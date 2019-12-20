import logging
import os
from datetime import date, datetime

from .schema import fetch_pattern, fetch_schema, get_resolver

logger = logging.getLogger(__name__)


def merge_config(destination, source):
    '''
    Credit: https://stackoverflow.com/a/20666342
    '''

    if isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                merge_config(node, value)
            else:
                destination[key] = value

    return destination


def parse_version(version):
    if version:
        try:
            datetime.strptime(version, '%Y%m%d')
            return version
        except ValueError:
            raise ValueError("Incorrect version format, should be YYYYMMDD")
    elif version is False:
        return date.today().strftime('%Y%m%d')
    else:
        return None


def parse_config(path, version=None):
    path_components = path.strip(os.sep).split(os.sep)

    try:
        schema_path = os.sep.join(path_components[:3]) + '.json'
    except IndexError:
        return False

    pattern = fetch_pattern(schema_path)
    schema = fetch_schema(schema_path)
    resolver = get_resolver(schema_path, schema)

    # collect environment variables starting with ISIMIP_ as attributes
    attributes = {}
    for key in os.environ:
        if key.startswith('ISIMIP_'):
            attribute = key.replace('ISIMIP_', '').lower()
            attributes[attribute] = os.environ[key]

    config = {
        'path': path,
        'version': version,
        'schema_path': schema_path,
        'pattern': pattern,
        'schema': schema,
        'resolver': resolver,
        'attributes': attributes
    }

    logger.debug(config)
    return config


def parse_filelist(filelist_file):
    if filelist_file:
        with open(filelist_file) as f:
            filelist = f.read().splitlines()
    else:
        filelist = None

    logger.debug('filelist = %s', filelist)
    return filelist
