import logging
import os
from datetime import date, datetime
from pathlib import Path

from .fetch import fetch_pattern, fetch_schema

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


def parse_filelist(filelist_file):
    if filelist_file:
        with open(filelist_file) as f:
            filelist = f.read().splitlines()
    else:
        filelist = None

    logger.debug('filelist = %s', filelist)
    return filelist


def load_pattern(path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        schema_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')

        pattern = fetch_pattern(schema_path)
        if pattern:
            return pattern

    return None


def load_schema(path):
    path_components = path.strip(os.sep).split(os.sep)
    for i in range(len(path_components), 0, -1):
        schema_path = Path(os.sep.join(path_components[:i+1])).with_suffix('.json')

        schema = fetch_schema(schema_path)
        if schema:
            return schema

    return None
