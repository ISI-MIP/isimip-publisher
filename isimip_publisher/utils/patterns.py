import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def match_datasets(config, base_path, files):
    dataset_dict = {}

    for file in files:
        file_abspath = base_path / file

        file_path, file_name, identifiers = match_file(config, file_abspath)
        dataset_path, dataset_name, _ = match_dataset(config, file_abspath)

        if dataset_path not in dataset_dict:
            dataset_dict[dataset_path] = {
                'name': dataset_name,
                'path': dataset_path,
                'abspath': Path(file.replace(str(file_path), str(dataset_path))),
                'identifiers': identifiers,
                'files': []
            }

        dataset_dict[dataset_path]['files'].append({
            'name': file_name,
            'path': file_path,
            'abspath': file_abspath,
            'dataset_path': dataset_path,
            'identifiers': identifiers
        })

    dataset_list = list(dataset_dict.values())
    return dataset_list


def match_files(config, base_path, files):
    file_list = []

    for file in files:
        file_abspath = base_path / file

        file_path, file_name, identifiers = match_file(config, file_abspath)
        dataset_path, dataset_name, _ = match_dataset(config, file_abspath)

        file_list.append({
            'name': file_name,
            'path': file_path,
            'abspath': file_abspath,
            'dataset_path': dataset_path,
            'identifiers': identifiers
        })

    return file_list


def match_dataset(config, file_abspath):
    return match(config, file_abspath, 'path', 'dataset')


def match_file(config, file_abspath):
    return match(config, file_abspath, 'path', 'file')


def match(config, file_abspath, dirname_pattern_key, filename_pattern_key):
    dirname_pattern = config['pattern'][dirname_pattern_key]
    filename_pattern = config['pattern'][filename_pattern_key]

    # match the dirname and the filename
    dirname_match, dirname_identifiers = match_string(dirname_pattern, str(file_abspath.parent))
    filename_match, filename_identifiers = match_string(filename_pattern, str(file_abspath.name))

    path = Path(dirname_match) / filename_match
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
