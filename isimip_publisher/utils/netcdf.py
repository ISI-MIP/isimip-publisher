import logging
from datetime import datetime

import numpy as np
from netCDF4 import Dataset

logger = logging.getLogger(__name__)

FLOAT_TYPES = [np.float32, np.float64]
INT_TYPES = [np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32, np.int64, np.uint64]


def get_netcdf_dimensions(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        return {
            dimension_name: dimension.size
            for dimension_name, dimension in rootgrp.dimensions.items()
        }


def get_netcdf_variables(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        variables = {}
        for variable_name, variable in rootgrp.variables.items():
            variables[variable_name] = {}
            for key, value in variable.__dict__.items():
                if type(value) in FLOAT_TYPES:
                    value = float(value)
                elif type(value) in INT_TYPES:
                    value = int(value)
                variables[variable_name][key] = value
        return variables


def get_netcdf_global_attributes(file_path):
    with Dataset(file_path, 'r', format='NETCDF4') as rootgrp:
        global_attributes = {}
        for key, value in rootgrp.__dict__.items():
            if type(value) in FLOAT_TYPES:
                value = float(value)
            elif type(value) in INT_TYPES:
                value = int(value)
            global_attributes[key] = value
        return global_attributes


def update_netcdf_global_attributes(file_path, set_attributes={}, delete_attributes=[]):
    with Dataset(file_path, 'a', format='NETCDF4') as rootgrp:
        for attr in rootgrp.__dict__:
            if attr in delete_attributes:
                logger.debug('delete %s in %s', attr, file_path)
                rootgrp.delncattr(attr)

        for attr, value in set_attributes.items():
            logger.debug('set %s to %s in %s', attr, value, file_path)
            rootgrp.setncattr(attr, value2string(value))


def value2string(value):
    if isinstance(value, datetime):
        return value.isoformat() + 'Z',
    else:
        return str(value)
