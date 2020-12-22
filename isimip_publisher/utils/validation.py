from pathlib import Path


def validate_datasets(schema, datasets):
    for dataset in datasets:
        dataset.validate(schema)

        for file in dataset.files:
            file.validate(schema)


def check_datasets(datasets, db_datasets):
    assert len(datasets) == len(db_datasets), \
        'Length mismatch {} != {}'.format(len(datasets), len(db_datasets))

    for dataset, db_dataset in zip(datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            # check file
            assert file.path == db_file.path, \
                'Path mismatch {} != {} for file {}'.format(file.path, db_file.path, db_file.id)

            if file.uuid:
                assert str(file.uuid) == db_file.id, \
                    'UUID mismatch {} != {} for file {}'.format(file.uuid, db_file.id, db_file.id)

            # patch checksum_type in order to compute checksum with a non default checksum_type
            file.checksum_type = db_file.checksum_type
            assert file.checksum == db_file.checksum, \
                'Checksum mismatch {} != {} for file {}'.format(file.checksum, db_file.checksum, db_file.id)

            # check if the specifiers match
            assert file.specifiers == db_file.specifiers, \
                'Specifier mismatch {} != {} for file {}'.format(file.specifiers, db_file.specifiers, db_file.id)

            # check the files
            file_path = Path(file.abspath)
            assert file_path.is_file(), \
                '{} does not exist'.format(file_path)

            for suffix in ['.json', '.png']:
                assert file_path.with_suffix(suffix).is_file(), \
                    '{} does not exist'.format(file_path.with_suffix(suffix))

        # check dataset
        assert dataset.path == db_dataset.path, \
            'Path mismatch {} != {} for dataset {}'.format(dataset.path, db_dataset.path, db_dataset.id)

        # check if the specifiers match
        assert dataset.specifiers == db_dataset.specifiers, \
            'Specifier mismatch {} != {} for dataset {}'.format(dataset.specifiers, db_dataset.specifiers, db_dataset.id)
