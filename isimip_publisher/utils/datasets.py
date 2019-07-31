import os
import re


def find_datasets(config, files):
    dataset_pattern = config['dataset_pattern'].replace(os.linesep, '')

    datasets = {}

    for file_path in files:
        file_name = os.path.basename(file_path)
        match = re.search(dataset_pattern, file_name)

        assert match is not None, 'No dataset match for %s' % file_path

        dataset = match.group(0)

        if dataset not in datasets:
            datasets[dataset] = []

        datasets[dataset].append(file_name)

    return datasets
