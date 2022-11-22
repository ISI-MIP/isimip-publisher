import logging

from isimip_utils.patterns import match_dataset_path, match_file_path
from isimip_utils.exceptions import DidNotMatch
from isimip_utils.utils import exclude_path, include_path

from ..models import Dataset, File

logger = logging.getLogger(__name__)


def match_datasets(pattern, base_path, files, include=None, exclude=None):
    dataset_dict = {}

    # first pass: find datasets
    for file in files:
        if include_path(include, file) and not exclude_path(exclude, file):
            # construct absolute path
            file_abspath = base_path / file
            logger.info('match_datasets %s', file_abspath)

            # match dataset
            dataset_path, dataset_specifiers = match_dataset_path(pattern, file_abspath)

            # add dataset to list of dataset, if it was not found before
            if dataset_path not in dataset_dict:
                dataset_dict[dataset_path] = Dataset(
                    name=dataset_path.name,
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
            dataset_path, dataset_specifiers = match_dataset_path(pattern, file_abspath)
        except DidNotMatch:
            # skip the file if not dataset pattern matches
            continue

        if dataset_path in dataset_dict:
            if not exclude_path(exclude, file):
                # if the file is not explicitely excluded, match the file pattern
                file_path, file_specifiers = match_file_path(pattern, file_abspath)
                logger.debug(dataset_specifiers)
                logger.debug(file_specifiers)

                # append file to dataset
                dataset_dict[dataset_path].files.append(File(
                    dataset=dataset_dict[dataset_path],
                    name=file_path.name,
                    path=file_path.as_posix(),
                    abspath=file_abspath.as_posix(),
                    specifiers=file_specifiers
                ))

            else:
                # remove datasets which have files which are excluded
                dataset_dict[dataset_path].exclude = True

    # sort datasets and files and return
    dataset_list = sorted([dataset for dataset in dataset_dict.values() if not dataset.exclude], key=lambda dataset: dataset.path)
    for dataset in dataset_list:
        dataset.files = sorted(dataset.files, key=lambda file: file.path)

    return dataset_list


def filter_datasets(db_datasets, include=None, exclude=None):
    datasets = []
    for db_dataset in db_datasets:
        db_files = [file.path for file in db_dataset.files]
        if any([include_path(include, file) for file in db_files]) \
                and not any([exclude_path(exclude, file) for file in db_files]):
            datasets.append(db_dataset)

    return datasets
