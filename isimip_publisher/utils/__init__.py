import os
import logging

from collections import OrderedDict

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_env():
    load_dotenv(os.path.join(os.getcwd(), '.env'))


def setup_logging():
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))


def order_dict(unsorted):
    return OrderedDict([(key, unsorted[key]) for key in sorted(unsorted)])


def get_subparser_title(module):
    return module.split('.')[-1]
