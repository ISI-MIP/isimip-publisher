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


def check_datasets(datasets, db_datasets, skip_checksum=False):
    if len(datasets) != len(db_datasets):
        logger.error(f'Length mismatch {len(datasets)} != {len(db_datasets)}')

    for dataset, db_dataset in zip(datasets, db_datasets, strict=True):
        for file, db_file in zip(dataset.files, db_dataset.files, strict=True):
            # check the actual file
            file_path = Path(file.abspath)
            if file_path.is_file():
                if not skip_checksum:
                    # compute the checksum
                    computed_checksum = get_checksum(file.abspath, file.checksum_type)

                    # check file checksum consistency
                    if computed_checksum == db_file.checksum:
                        logger.info(f'Checksum match for file {db_file.path}')
                    else:
                        logger.error(f'Checksum mismatch {file.checksum} != {computed_checksum} '
                                     f'for file {db_file.path}')

                # check file path consistency
                if file.path != db_file.path:
                    logger.error(f'Path mismatch {file.path} != {db_file.path} for file {db_file.path}')

                # check file uuid consistency
                if file.uuid:
                    db_uuid = db_file.target_id or db_file.id
                    if str(file.uuid) != str(db_uuid):
                        logger.error(f'UUID mismatch {file.uuid} != {db_uuid} for file {db_file.path}')

                # check file specifiers consistency
                if file.specifiers != db_file.specifiers:
                    logger.error(f'Specifier mismatch {format_json(file.specifiers)} !='
                                 f' {format_json(db_file.specifiers)} for file {db_file.path}')
            else:
                logger.error(f'{file_path} does not exist')

            # check the json file
            if file_path.with_suffix('.json').is_file():
                # open json file
                metadata = json.loads(file_path.with_suffix('.json').read_text())

                # check json checksum consistency
                if metadata.get('checksum') != db_file.checksum:
                    logger.error(f"JSON checksum mismatch {metadata.get('checksum')} != {db_file.checksum}"
                                 f' for file {db_file.path}')

                # check json path consistency
                if metadata.get('path') != db_file.path:
                    logger.error(f"JSON path mismatch {metadata.get('path')} != {db_file.path} "
                                 f' for file {db_file.path}')

                # check json uuid consistency
                if metadata.get('id'):
                    db_uuid = db_file.target_id or db_file.id
                    if metadata.get('id') != str(db_uuid):
                        logger.error(f"JSON mismatch {metadata.get('id')} != {db_uuid} for file {db_file.path}")

                # check json specifiers consistency
                if metadata.get('specifiers') != db_file.specifiers:
                    logger.error(f"JSON specifier mismatch {format_json(metadata.get('specifiers'))} !="
                                 f' {format_json(db_file.specifiers)} for file {db_file.path}')
            else:
                logger.error(f'{file_path} does not exist')

        # check dataset
        if dataset.path != db_dataset.path:
            logger.error(f'Path mismatch {dataset.path} != {db_dataset.path} for dataset {db_dataset.id}')

        # check if the specifiers match
        if dict(dataset.specifiers) != dict(db_dataset.specifiers):
            logger.error(f'Specifier mismatch {format_json(dataset.specifiers)} !='
                         f' {format_json(db_dataset.specifiers)} for dataset {db_dataset.id}')


def format_json(data):
    return json.dumps({key: data[key] for key in sorted(data.keys())}, indent=2)
