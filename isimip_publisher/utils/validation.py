import json
from pathlib import Path

from isimip_utils.checksum import get_checksum


def validate_datasets(schema, path, datasets):
    assert datasets, f'no dataset found for {path}'

    for dataset in datasets:
        dataset.validate(schema)

        assert dataset.files, f'no files found for dataset {dataset.path}'
        for file in dataset.files:
            file.validate(schema)


def check_datasets(datasets, db_datasets):
    assert len(datasets) == len(db_datasets), \
        f'Length mismatch {len(datasets)} != {len(db_datasets)}'

    for dataset, db_dataset in zip(datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            # check the actual file
            file_path = Path(file.abspath)
            assert file_path.is_file(), \
                f'{file_path} does not exist'

            # check the json file
            assert file_path.with_suffix('.json').is_file(), \
                f'{file_path} does not exist'

            # compute the checksum
            computed_checksum = get_checksum(file.abspath, file.checksum_type)

            # check file checksum consitency
            assert computed_checksum == db_file.checksum, \
                f'Checksum mismatch {file.checksum} != {computed_checksum} for file {db_file.id}'

            # check file path consitency
            assert file.path == db_file.path, \
                f'Path mismatch {file.path} != {db_file.path} for file {db_file.id}'

            # check file uuid consitency
            if file.uuid:
                assert str(file.uuid) == db_file.id, \
                    f'UUID mismatch {file.uuid} != {db_file.id} for file {db_file.id}'

            # check file specifiers consitency
            assert file.specifiers == db_file.specifiers, \
                f'Specifier mismatch {file.specifiers} != {db_file.specifiers} for file {db_file.id}'

            # open json file
            metadata = json.loads(file_path.with_suffix('.json').read_text())

            # check json checksum consitency
            assert metadata.get('checksum') == db_file.checksum, \
                'Checksum mismatch {} != {} for file {}'.format(metadata.get('checksum'), computed_checksum, db_file.id)

            # check json path consitency
            assert metadata.get('path') == db_file.path, \
                'Path mismatch {} != {} for file {}'.format(metadata.get('path'), db_file.path, db_file.id)

            # check json uuid consitency
            if metadata.get('id'):
                assert metadata.get('id') == db_file.id, \
                    'UUID mismatch {} != {} for file {}'.format(metadata.get('id'), db_file.id, db_file.id)

            # check json specifiers consitency
            assert metadata.get('specifiers') == db_file.specifiers, \
                'Specifier mismatch {} != {} for file {}'.format(metadata.get('specifiers'),
                                                                 db_file.specifiers, db_file.id)

        # check dataset
        assert dataset.path == db_dataset.path, \
            f'Path mismatch {dataset.path} != {db_dataset.path} for dataset {db_dataset.id}'

        # check if the specifiers match
        assert dataset.specifiers == db_dataset.specifiers, \
            f'Specifier mismatch {dataset.specifiers} != {db_dataset.specifiers} for dataset {db_dataset.id}'
