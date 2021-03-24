import json
from pathlib import Path

from .checksum import get_checksum


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
            # check the actual file
            file_path = Path(file.abspath)
            assert file_path.is_file(), \
                '{} does not exist'.format(file_path)

            # check the json file
            assert file_path.with_suffix('.json').is_file(), \
                '{} does not exist'.format(file_path)

            # compute the checksum
            computed_checksum = get_checksum(file.abspath, file.checksum_type)

            # check file checksum consitency
            assert computed_checksum == db_file.checksum, \
                'Checksum mismatch {} != {} for file {}'.format(file.checksum, computed_checksum, db_file.id)

            # check file path consitency
            assert file.path == db_file.path, \
                'Path mismatch {} != {} for file {}'.format(file.path, db_file.path, db_file.id)

            # check file uuid consitency
            if file.uuid:
                assert str(file.uuid) == db_file.id, \
                    'UUID mismatch {} != {} for file {}'.format(file.uuid, db_file.id, db_file.id)

            # check file specifiers consitency
            assert file.specifiers == db_file.specifiers, \
                'Specifier mismatch {} != {} for file {}'.format(file.specifiers, db_file.specifiers, db_file.id)

            # open json file
            metadata = json.loads(file_path.with_suffix('.json').read_text())

            # check json checksum consitency
            assert metadata.get('checksum') == db_file.checksum, \
                'Checksum mismatch {} != {} for file {}'.format(metadata.get('checksum'), computed_checksum, db_file.id)

            # check json path consitency
            assert metadata.get('path') == db_file.path, \
                'Path mismatch {} != {} for file {}'.format(metadata.get('path'), db_file.path, db_file.id)

            # check json uuid consitency
            if file.uuid:
                assert metadata.get('id') == db_file.id, \
                    'UUID mismatch {} != {} for file {}'.format(metadata.get('id'), db_file.id, db_file.id)

            # check json specifiers consitency
            assert metadata.get('specifiers') == db_file.specifiers, \
                'Specifier mismatch {} != {} for file {}'.format(metadata.get('specifiers'), db_file.specifiers, db_file.id)

        # check dataset
        assert dataset.path == db_dataset.path, \
            'Path mismatch {} != {} for dataset {}'.format(dataset.path, db_dataset.path, db_dataset.id)

        # check if the specifiers match
        assert dataset.specifiers == db_dataset.specifiers, \
            'Specifier mismatch {} != {} for dataset {}'.format(dataset.specifiers, db_dataset.specifiers, db_dataset.id)
