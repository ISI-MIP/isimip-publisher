import logging
import os
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_env():
    load_dotenv(Path().cwd() / '.env')


def setup_logging():
    filename = os.getenv('LOG_FILE')
    level = os.getenv('LOG_LEVEL', 'ERROR')
    if filename:
        logging.basicConfig(level=level, filename=filename)
    else:
        logging.basicConfig(level=level)


def order_dict(unsorted):
    return OrderedDict([(key, unsorted[key]) for key in sorted(unsorted)])


def get_subparser_title(module):
    return module.split('.')[-1]
