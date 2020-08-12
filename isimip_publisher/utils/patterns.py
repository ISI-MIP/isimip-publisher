import logging
from pathlib import Path

from ..models import Dataset, File

logger = logging.getLogger(__name__)


def match_datasets(pattern, base_path, files):
    dataset_dict = {}

    for file in files:
        file_abspath = base_path / file

        logger.info('match_datasets %s', file_abspath)

        file_path, file_name, file_identifiers = match_file(pattern, file_abspath)
        dataset_path, dataset_name, dataset_identifiers = match_dataset(pattern, file_abspath)

        if dataset_path not in dataset_dict:
            dataset_dict[dataset_path] = Dataset(
                name=dataset_name,
                path=dataset_path,
                attributes=file_identifiers
            )

        dataset_dict[dataset_path].files.append(File(
            dataset=dataset_dict[dataset_path],
            name=file_name,
            path=file_path,
            abspath=file_abspath,
            attributes=dataset_identifiers
        ))

    # sort datasets and files and return
    dataset_list = sorted(dataset_dict.values(), key=lambda d: str(d.path))
    for dataset in dataset_list:
        dataset.files = sorted(dataset.files, key=lambda f: str(f.path))

    return dataset_list


def match_dataset(pattern, file_abspath):
    return match(pattern, file_abspath, 'path', 'dataset')


def match_file(pattern, file_abspath):
    return match(pattern, file_abspath, 'path', 'file')


def match(pattern, file_abspath, dirname_pattern_key, filename_pattern_key):
    dirname_pattern = pattern[dirname_pattern_key]
    filename_pattern = pattern[filename_pattern_key]

    # match the dirname and the filename
    dirname_match, dirname_identifiers = match_string(dirname_pattern, str(file_abspath.parent))
    filename_match, filename_identifiers = match_string(filename_pattern, str(file_abspath.name))

    path = Path(dirname_match) / filename_match
    name = filename_match

    # assert that any value in dirname_identifiers at least starts with
    # its corresponding value (same key) in filename_identifiers
    # e.g. 'ewe' and 'ewe_north-sea'
    for key, value in filename_identifiers.items():
        if key in dirname_identifiers:
            f, d = filename_identifiers[key], dirname_identifiers[key]
            assert d.lower().startswith(f.lower()), (f, d)

    return path, name, {**dirname_identifiers, **filename_identifiers}


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
