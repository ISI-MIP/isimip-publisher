import logging
import os

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
    return match(config, file_path, 'path', 'dataset')


def match_file(config, file_path):
    return match(config, file_path, 'path', 'file')


def match(config, file_path, dirname_pattern_key, filename_pattern_key):
    dirname_pattern = config['pattern'][dirname_pattern_key]
    filename_pattern = config['pattern'][filename_pattern_key]

    # split file path
    dirname, filename = os.path.split(file_path)

    # match the dirname and the filename
    dirname_match, dirname_identifiers = match_string(dirname_pattern, dirname)
    filename_match, filename_identifiers = match_string(filename_pattern, filename)

    path = os.path.join(dirname_match, filename_match)
    name = filename_match
    identifiers = {**dirname_identifiers, **filename_identifiers}

    return path, name, identifiers


def match_string(pattern, string):
    logger.debug(pattern.pattern)
    logger.debug(string)

    # try to match the string
    match = pattern.search(string)
    assert match is not None, 'No match for %s' % string

    identifiers = {}
    for key, value in match.groupdict().items():
        if value is not None:
            if value.isdigit():
                identifiers[key] = int(value)
            else:
                identifiers[key] = value

    return match.group(0), identifiers
