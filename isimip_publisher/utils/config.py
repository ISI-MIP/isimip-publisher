import logging
import os
from datetime import date, datetime
from pathlib import Path

from .schema import fetch_pattern, fetch_schema

logger = logging.getLogger(__name__)


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

    pattern, schema = None, None
    for i in range(len(path_components), 0, -1):
        schema_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')

        if pattern is None:
            pattern = fetch_pattern(schema_path)

        if schema is None:
            schema = fetch_schema(schema_path)

    if pattern and schema:
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
            'attributes': attributes
        }

        logger.debug(config)
        return config

    return False


def parse_filelist(filelist_file):
    if filelist_file:
        with open(filelist_file) as f:
            filelist = f.read().splitlines()
    else:
        filelist = None

    logger.debug('filelist = %s', filelist)
    return filelist
