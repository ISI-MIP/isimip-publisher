from .patterns import match_dataset


def find_datasets(config, files):
    datasets = {}

    for file_path in files:
        dataset, identifiers = match_dataset(config, file_path)

        if dataset not in datasets:
            datasets[dataset] = identifiers

    return datasets
