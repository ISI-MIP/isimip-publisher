import logging
from datetime import datetime

from netCDF4 import Dataset

from . import order_dict

logger = logging.getLogger(__name__)


def get_netcdf_dimensions(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.dimensions


def get_netcdf_variables(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.variables


def get_netcdf_global_attributes(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.__dict__


def update_netcdf_global_attributes(config, metadata, file_path):
    logger.info('update %s', file_path)

    with Dataset(file_path, 'a', format='NETCDF4') as rootgrp:
        # remove all attributes, but keep some
        for attr in rootgrp.__dict__:
            if attr not in config['netcdf_metadata_keep']:
                logger.debug('delete %s in %s', attr, file_path)
                rootgrp.delncattr(attr)

        for attr, value in order_dict(metadata).items():
            logger.debug('set %s to %s in %s', attr, value, file_path)
            rootgrp.setncattr(attr, value2string(value))


def value2string(value):
    if isinstance(value, datetime):
        return value.isoformat() + 'Z',
    else:
        return str(value)
