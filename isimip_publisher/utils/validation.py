import os
import re


def validate_file_path(config, file):
    # compile patterns
    dirname_pattern = re.compile(config['dirname_pattern'])
    filename_pattern = re.compile(config['filename_pattern'])

    # split file path
    dirname, filename = os.path.split(file)

    # try to match the dirname
    dirmatch = dirname_pattern.search(dirname)
    assert dirmatch is not None, 'No directory match for %s' % dirname

    dirgroups = dirmatch.groupdict()
    for key, value in dirgroups.items():
        if key == 'sector':

            assert value == config['sector'], \
                '%s mismatch: %s != %s for %s' % \
                (key, value, config['sector'], file)

        elif key == 'model':

            assert value == config['model'], \
                '%s mismatch: %s != %s for %s' % \
                (key, value, config['model'], file)

        elif key in config['dirname_validation']:
            values = config[config['dirname_validation'][key]]

            assert value in values, \
                '%s mismatch: %s not in %s for %s' % \
                (key, value, values, file)

    # try to match the filename
    filematch = filename_pattern.match(filename)
    assert filematch is not None, 'No filename match for %s' % filename

    filegroups = filematch.groupdict()
    for key, value in filegroups.items():
        if key == 'sector':

            assert value == config['sector'].lower(), \
                '%s mismatch: %s != %s for %s' % \
                (key, value, config['sector'], file)

        elif key == 'model':

            assert value == config['model'].lower(), \
                '%s mismatch: %s != %s for %s' % \
                (key, value, config['model'], file)

        elif key in config['filename_validation']:
            values = config[config['filename_validation'][key]]

            assert value in values, \
                '%s mismatch: %s not in %s for %s' % \
                (key, value, values, file)

    dirgroups.update(filegroups)
    return dirgroups


def validate_file(config, file):
    return validate_file_path(config, file)
