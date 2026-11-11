def print_files(files, exclude=None):
    for file_path in sorted(files):
        if exclude is None or file_path not in exclude:
            print(file_path)


def print_datasets_files(datasets):
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def print_datasets_files_count(datasets):
    print(len([file for dataset in datasets for file in dataset.files]))
