import logging

from datetime import datetime

from netCDF4 import Dataset

from isimip_publisher.utils import order_dict

logger = logging.getLogger(__name__)


def get_netcdf_dimensions(file):
    with Dataset(file, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.dimensions


def get_netcdf_variables(file):
    with Dataset(file, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.variables


def get_netcdf_global_attributes(file):
    with Dataset(file, 'r', format='NETCDF4') as rootgrp:
        return rootgrp.__dict__


def update_netcdf_global_attributes(config, metadata, file):
    # filter metadata according to config
    metadata = {key: value for key, value in metadata.items() if key in list(config['netcdf_metadata'])}

    with Dataset(file, 'a', format='NETCDF4') as rootgrp:
        # remove all attributes, but keep some
        for attr in rootgrp.__dict__:
            if attr in config['netcdf_metadata'] and attr not in metadata:
                metadata[attr] = rootgrp.getncattr(attr)

            logger.debug('delete %s in %s', attr, file)
            rootgrp.delncattr(attr)

        for attr, value in order_dict(metadata).items():
            logger.debug('set %s to %s in %s', attr, value, file)
            rootgrp.setncattr(attr, value2string(value))


def value2string(value):
    if isinstance(value, datetime):
        return value.isoformat() + 'Z',
    else:
        return str(value)
