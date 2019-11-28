import logging
import os
from datetime import date, datetime

import yaml

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


def parse_path(path):
    return path.strip(os.sep).split(os.sep)


def parse_config(path, path_components, version=None):
    config_dir = os.environ['CONFIG_DIR']

    config = {
        'path': path,
        'version': version
    }

    # parse yaml config files
    config_files = [
        os.path.join(config_dir, '_default.yml'),
        os.path.join(config_dir, path_components[0], '_default.yml'),
        os.path.join(config_dir, path_components[0], path_components[1], '_default.yml'),
        os.path.join(config_dir, path_components[0], path_components[1], path_components[2] + '.yml')
    ]

    for config_file in config_files:
        try:
            with open(config_file) as f:
                file_config = yaml.safe_load(f.read())
                merge_config(config, file_config)

        except OSError as e:
            logger.error(e)
            raise e

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
