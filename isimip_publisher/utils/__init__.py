import logging
import os
import re

from collections import OrderedDict

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_env():
    load_dotenv(os.path.join(os.getcwd(), '.env'))


def setup_logging():
    filename = os.getenv('LOG_FILE')
    level = os.getenv('LOG_LEVEL', 'INFO')
    if filename:
        logging.basicConfig(level=level, filename=filename)
    else:
        logging.basicConfig(level=level)


def order_dict(unsorted):
    return OrderedDict([(key, unsorted[key]) for key in sorted(unsorted)])


def get_subparser_title(module):
    return module.split('.')[-1]


def add_version_to_path(path, version):
    root, ext = os.path.splitext(path)

    # check if there is already a version
    match = re.search('(\\d{8})$', root)
    if match:
        assert version == match.group(1), \
            'version mismatch in %s' % path

        # version string was already added
        return path
    else:
        return '%s_%s%s' % (root, version, ext)
