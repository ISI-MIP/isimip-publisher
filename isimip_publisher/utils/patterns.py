import logging
from collections import OrderedDict
from pathlib import Path

from ..models import Dataset, File

logger = logging.getLogger(__name__)


def match_datasets(pattern, base_path, files, include=None, exclude=None):
    dataset_dict = {}

    # first pass: find datasets
    for file in files:
        if not (exclude and match_path(exclude, file)) and \
           not (include and not match_path(include, file)):
            # construct absolute path
            file_abspath = base_path / file
            logger.info('match_datasets %s', file_abspath)

            # match dataset
            dataset_path, dataset_name, dataset_specifiers = match_dataset(pattern, file_abspath)

            # add dataset to list of dataset, if it was not found before
            if dataset_path not in dataset_dict:
                dataset_dict[dataset_path] = Dataset(
                    name=dataset_name,
                    path=dataset_path.as_posix(),
                    specifiers=dataset_specifiers
                )

    # second path: add files to datasets
    # the full list is used here to include also files for the dataset which are not explicitely included
    # datasets which
    for file in files:
        # construct absolute path
        file_abspath = base_path / file
        logger.info('match_files %s', file_abspath)

        # try to find a dataset for this file
        try:
            dataset_path, dataset_name, dataset_specifiers = match_dataset(pattern, file_abspath)
            if dataset_path in dataset_dict:
                if not (exclude and match_path(exclude, file)):
                    # if the file is not explicitely excluded, match the file pattern
                    file_path, file_name, file_specifiers = match_file(pattern, file_abspath)
                    logger.debug(dataset_specifiers)
                    logger.debug(file_specifiers)

                    # append file to dataset
                    dataset_dict[dataset_path].files.append(File(
                        dataset=dataset_dict[dataset_path],
                        name=file_name,
                        path=file_path.as_posix(),
                        abspath=file_abspath.as_posix(),
                        specifiers=file_specifiers
                    ))

                else:
                    # remove datasets which have files which are excluded
                    dataset_dict[dataset_path].exclude = True
        except AssertionError:
            # skip the file if not dataset pattern matches
            pass

    # sort datasets and files and return
    dataset_list = sorted([dataset for dataset in dataset_dict.values() if not dataset.exclude], key=lambda dataset: dataset.path)
    for dataset in dataset_list:
        dataset.files = sorted(dataset.files, key=lambda file: file.path)

    return dataset_list


def filter_datasets(db_datasets, include=None, exclude=None):
    datasets = []
    for db_dataset in db_datasets:
        db_files = [file.path for file in db_dataset.files]
        if not (exclude and match_paths(exclude, db_files)) and \
           not (include and not match_paths(include, db_files)):
            datasets.append(db_dataset)

    return datasets


def match_paths(path_set, file_paths):
    return any(match_path(path_set, file_path) for file_path in file_paths)


def match_path(path_set, file_path):
    if path_set:
        for path in path_set:
            if str(file_path).startswith(path):
                return True

    return False


def match_dataset(pattern, file_abspath):
    return match(pattern, file_abspath, 'path', 'dataset')


def match_file(pattern, file_abspath):
    return match(pattern, file_abspath, 'path', 'file')


def match(pattern, file_abspath, dirname_pattern_key, filename_pattern_key):
    dirname_pattern = pattern[dirname_pattern_key]
    filename_pattern = pattern[filename_pattern_key]

    # match the dirname and the filename
    dirname_match, dirname_specifiers = match_string(dirname_pattern, file_abspath.parent.as_posix())
    filename_match, filename_specifiers = match_string(filename_pattern, file_abspath.name)

    path = Path(dirname_match) / filename_match
    name = filename_match

    # assert that any value in dirname_specifiers at least starts with
    # its corresponding value (same key) in filename_specifiers
    # e.g. 'ewe' and 'ewe_north-sea'
    for key, value in filename_specifiers.items():
        if key in dirname_specifiers:
            f, d = filename_specifiers[key], dirname_specifiers[key]
            assert d.lower().startswith(f.lower()), \
                'dirname_specifier "{}" does not match filename_specifier "{}" in {}'.format(d, f, file_abspath)

    # merge filename_specifiers and dirname_specifiers
    specifiers = {**dirname_specifiers, **filename_specifiers}

    # apply specifiers_map if it exists
    if pattern['specifiers_map']:
        for key, value in specifiers.items():
            if value in pattern['specifiers_map']:
                specifiers[key] = pattern['specifiers_map'][value]

    # add fixed specifiers
    specifiers.update(pattern['specifiers'])

    return path, name, specifiers


def match_string(pattern, string):
    logger.debug(pattern.pattern)
    logger.debug(string)

    # try to match the string
    match = pattern.search(string)
    assert match is not None, 'No match for {} ("{}")'.format(string, pattern.pattern)

    specifiers = OrderedDict()
    for key, value in match.groupdict().items():
        if value is not None:
            if value.isdigit():
                specifiers[key] = int(value)
            else:
                specifiers[key] = value

    return match.group(0), specifiers
