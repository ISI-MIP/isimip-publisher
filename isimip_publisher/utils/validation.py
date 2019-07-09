import os
import re

from isimip_publisher.utils.netcdf import (
    get_netcdf_dimensions
)


def get_pattern(pattern_list):
    return re.compile(''.join(pattern_list))


def validate_file_path(config, file):
    dirname, filename = os.path.split(file)

    dirname_pattern = get_pattern(config['dirname_pattern'])
    match = dirname_pattern.search(dirname)
    assert match is not None, 'No directory match for %s' % dirname
    dirname_groups = match.groupdict()

    filename_pattern = get_pattern(config['filename_pattern'])
    match = filename_pattern.match(filename)
    assert match is not None, 'No filename match for %s' % filename
    filename_groups = match.groupdict()

    assert dirname_groups['sector'] == config['sector'], \
        'Sector mismatch: %s != %s for %s' % \
        (dirname_groups['sector'], config['sector'], file)

    assert dirname_groups['model'].lower() == filename_groups['model'], \
        'Model mismatch: %s != %s for %s' % \
        (dirname_groups['model'].lower(), filename_groups['model'], file)

    assert filename_groups['model'] in config['models'], \
        'Model mismatch: %s not in %s for %s' % \
        (filename_groups['model'], list(config['models']), file)

    dirname_groups.update(filename_groups)
    return dirname_groups


def validate_file(config, file):
    identifiers = validate_file_path(config, file)

    netcdf_dimensions = list(get_netcdf_dimensions(file))

    assert config['dimensions'] == netcdf_dimensions, \
        'Dimensions do not match (%s != %s) for %s' % \
        (config['dimensions'], netcdf_dimensions, file)

    return identifiers
