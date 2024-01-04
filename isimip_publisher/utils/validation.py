import json
import logging
from pathlib import Path

from isimip_utils.checksum import get_checksum

logger = logging.getLogger(__name__)

def validate_datasets(schema, path, datasets):
    if not datasets:
        raise RuntimeError(f'no dataset found for {path}')

    for dataset in datasets:
        dataset.validate(schema)

        if not dataset.files:
            raise RuntimeError(f'no files found for dataset {dataset.path}')

        for file in dataset.files:
            file.validate(schema)


def check_datasets(datasets, db_datasets):
    if len(datasets) != len(db_datasets):
        logger.error(f'Length mismatch {len(datasets)} != {len(db_datasets)}')

    for dataset, db_dataset in zip(datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            # check the actual file
            file_path = Path(file.abspath)
            if file_path.is_file():
                # compute the checksum
                computed_checksum = get_checksum(file.abspath, file.checksum_type)

                # check file checksum consitency
                if computed_checksum != db_file.checksum:
                    logger.error(f'Checksum mismatch {file.checksum} != {computed_checksum} for file {db_file.id}')

                # check file path consitency
                if file.path != db_file.path:
                    logger.error(f'Path mismatch {file.path} != {db_file.path} for file {db_file.id}')

                # check file uuid consitency
                if file.uuid:
                    if str(file.uuid) != db_file.id:
                        logger.error(f'UUID mismatch {file.uuid} != {db_file.id} for file {db_file.id}')

                # check file specifiers consitency
                if file.specifiers != db_file.specifiers:
                    logger.error(f'Specifier mismatch {file.specifiers} != {db_file.specifiers}'
                                  ' for file {db_file.id}')
            else:
                logger.error(f'{file_path} does not exist')

            # check the json file
            if file_path.with_suffix('.json').is_file():
                # open json file
                metadata = json.loads(file_path.with_suffix('.json').read_text())

                # check json checksum consitency
                if metadata.get('checksum') != db_file.checksum:
                    logger.error('Checksum mismatch {} != {} for file {}'.format(
                        metadata.get('checksum'), computed_checksum, db_file.id
                    ))

                # check json path consitency
                if metadata.get('path') != db_file.path:
                    logger.error('Path mismatch {} != {} for file {}'.format(
                        metadata.get('path'), db_file.path, db_file.id
                    ))

                # check json uuid consitency
                if metadata.get('id'):
                    if metadata.get('id') != db_file.id:
                        logger.error('UUID mismatch {} != {} for file {}'.format(
                            metadata.get('id'), db_file.id, db_file.id
                        ))

                # check json specifiers consitency
                if metadata.get('specifiers') != db_file.specifiers:
                    logger.error('Specifier mismatch {} != {} for file {}'.format(
                        metadata.get('specifiers'), db_file.specifiers, db_file.id
                    ))
            else:
                logger.error(f'{file_path} does not exist')

        # check dataset
        if dataset.path != db_dataset.path:
            logger.error(f'Path mismatch {dataset.path} != {db_dataset.path} for dataset {db_dataset.id}')

        # check if the specifiers match
        if dataset.specifiers != db_dataset.specifiers:
            logger.error(f'Specifier mismatch {dataset.specifiers} != {db_dataset.specifiers}'
                          ' for dataset {db_dataset.id}')
