import logging

import jsonschema

logger = logging.getLogger(__name__)


def validate_identifiers(schema, identifiers):
    logger.debug('identifiers = %s', identifiers)

    try:
        jsonschema.validate(schema=schema, instance=identifiers)
    except jsonschema.exceptions.ValidationError as e:
        logger.error('identifiers = %s', identifiers)
        raise e


def validate_datasets(datasets, database_datasets):
    assert len(datasets) == len(database_datasets)

    sorted_datasets = sorted(datasets, key=lambda d: d.path)
    for dataset, database_dataset in zip(sorted_datasets, database_datasets):
        assert str(dataset.path) == database_dataset.path, (str(dataset.path), database_dataset.path)
