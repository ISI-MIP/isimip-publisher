import logging
import os
import re

logger = logging.getLogger(__name__)


def validate_file_path(config, file):
    dirname_pattern = config['dirname_pattern'].replace(os.linesep, '')
    filename_pattern = config['filename_pattern'].replace(os.linesep, '')

    # split file path
    dirname, filename = os.path.split(file)

    # try to match the dirname
    logger.debug(dirname)
    logger.debug(dirname_pattern)
    dirmatch = re.search(dirname_pattern, dirname)
    assert dirmatch is not None, 'No directory match for %s' % dirname

    # get the identifiers from the match
    dirgroups = dirmatch.groupdict()
    logger.debug(dirgroups)

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
            values = config['dirname_validation'][key]

            assert value in values, \
                '%s mismatch: %s not in %s for %s' % \
                (key, value, values, file)

    # try to match the filename
    logger.debug(filename)
    logger.debug(filename_pattern)
    filematch = re.match(filename_pattern, filename)
    assert filematch is not None, 'No filename match for %s' % filename

    # get the identifiers from the match
    filegroups = filematch.groupdict()
    logger.debug(filegroups)

    for key, value in filegroups.items():
        if key == 'sector':

            assert value == config['sector'], \
                '%s mismatch: %s != %s for %s' % \
                (key, value, config['sector'], file)

        elif key == 'modelname':
            # compare with a modelname from the config or model.lower()
            model = config['model']
            modelname = config['models'][model].get('modelname', model.lower())

            assert value == modelname, \
                '%s mismatch: %s != %s for %s' % \
                (key, value, modelname, file)

        elif key in config['filename_validation']:
            values = config['filename_validation'][key]

            assert value in values, \
                '%s mismatch: %s not in %s for %s' % \
                (key, value, values, file)

    dirgroups.update(filegroups)
    return dirgroups


def validate_file(config, file):
    return validate_file_path(config, file)
