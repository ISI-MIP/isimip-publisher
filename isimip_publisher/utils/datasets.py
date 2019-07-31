import os
import re


def find_datasets(config, files):
    datasets = {}

    for file_path in files:
        dataset, identifiers = find_dataset_for_file(config, file_path)

        if dataset not in datasets:
            datasets[dataset] = identifiers

    return datasets


def find_dataset_for_file(config, file_path):
    dataset_pattern = config['dataset_pattern'].replace(os.linesep, '')

    file_name = os.path.basename(file_path)
    match = re.search(dataset_pattern, file_name)

    assert match is not None, 'No dataset match for %s' % file_path
    return match.group(0), match.groupdict()
