import os
import logging
import sys

import yaml

logger = logging.getLogger(__name__)


def merge_config(destination, source):
    '''
    Credit: https://stackoverflow.com/a/20666342
    '''

    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_config(node, value)
        else:
            destination[key] = value

    return destination


def parse_config(args):
    config_dir = os.environ['CONFIG_DIR']

    config = {
        'simulation_round': args.simulation_round,
        'sector': args.sector,
        'model': args.model
    }

    # parse yaml config files

    config_files = [
        os.path.join(config_dir, 'default.yml'),
        os.path.join(config_dir, args.simulation_round.lower(), 'default.yml'),
        os.path.join(config_dir, args.simulation_round.lower(), 'sectors', args.sector + '.yml')
    ]

    for config_file in config_files:
        try:
            with open(config_file) as f:
                try:
                    merge_config(config, yaml.safe_load(f.read()))
                except TypeError:
                    logger.error('%s is empty', config_file)
                    sys.exit()

        except OSError:
            logger.error('%s does not exist', config_file)
            sys.exit()

    # check model
    assert config['model'] in config['models'], \
        'Model %(model)s is not configured for %(simulation_round)s %(sector)s' % config

    logger.debug(config)
    return config


def parse_filelist(args):
    if args.filelist_file:
        with open(args.filelist_file) as f:
            filelist = f.read().splitlines()
    else:
        filelist = None

    logger.debug(filelist)
    return filelist
