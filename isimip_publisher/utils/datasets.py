import os

from .patterns import match_dataset


def find_datasets(config, files):
    datasets = {}

    for file_path in files:
        dir_name, file_name = os.path.split(file_path)
        dataset_name, identifiers = match_dataset(config, file_path)
        dataset_path = os.path.join(dir_name, dataset_name)

        if dataset_path not in datasets:
            datasets[dataset_path] = {
                'name': dataset_name,
                'identifiers': identifiers,
                'files': [file_name]
            }
        else:
            datasets[dataset_path]['files'].append(file_name)

    return datasets
