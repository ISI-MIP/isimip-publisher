import logging
import os
import re

logger = logging.getLogger(__name__)


def match_datasets(config, files):
    dataset_dict = {}

    for file_path in files:
        dataset_path, dataset_name, identifiers = match_dataset(config, file_path)

        if dataset_path not in dataset_dict:
            dataset_dict[dataset_path] = {
                'name': dataset_name,
                'abspath': os.path.join(os.path.dirname(file_path), dataset_name),
                'identifiers': identifiers,
                'files': [file_path]
            }
        else:
            dataset_dict[dataset_path]['files'].append(file_path)

    return dataset_dict


def match_files(config, files):
    file_dict = {}

    for file_abspath in files:
        file_path, file_name, identifiers = match_file(config, file_abspath)
        dataset_path, dataset_name, _ = match_dataset(config, file_abspath)

        file_dict[file_path] = {
            'name': file_name,
            'abspath': file_abspath,
            'identifiers': identifiers,
            'dataset_path': dataset_path
        }

    return file_dict


def match_dataset(config, file_path):
    return match(config, file_path, 'dirname_pattern', 'dataset_pattern')


def match_file(config, file_path):
    return match(config, file_path, 'dirname_pattern', 'filename_pattern')


def match(config, file_path, dirname_pattern_key, filename_pattern_key):
    dirname_pattern = config[dirname_pattern_key].replace(os.linesep, '')
    filename_pattern = config[filename_pattern_key].replace(os.linesep, '')

    # split file path
    dirname, filename = os.path.split(file_path)

    # match the dirname and the filename
    dirname_match, dirname_identifiers = match_string(dirname_pattern, dirname)
    filename_match, filename_identifiers = match_string(filename_pattern, filename)

    path = os.path.join(dirname_match, filename_match)
    name = filename_match
    identifiers = {**dirname_identifiers, **filename_identifiers}
    validate_identifiers(config, file_path, identifiers)

    return path, name, identifiers


def match_string(pattern, string):
    logger.debug(pattern)
    logger.debug(string)

    # try to match the string
    match = re.search(pattern, string)
    assert match is not None, 'No match for %s' % string
    return match.group(0), {key: value for key, value in match.groupdict().items() if value is not None}


def validate_identifiers(config, file_path, identifiers):
    for key, value in identifiers.items():
        validation_key = '%s_validation' % key

        if validation_key in config:
            values = config[validation_key]

            assert value in values, \
                '%s mismatch: %s not in %s for %s' % \
                (key, value, values, file_path)

        elif key == 'model':
            assert value in config['models'], \
                'Model %s is not configured.' % value

        elif key == 'modelname':
            assert (value == identifiers['model'].lower()
                    or value == config['models'].get(identifiers['model']).get('modelname')), \
                'Modelname %s is not configured.' % value
