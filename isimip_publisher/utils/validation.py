import logging

import jsonschema

logger = logging.getLogger(__name__)


def validate_dataset(config, dataset_path, dataset):
    return validate_identifiers(config, dataset_path, dataset['identifiers'])


def validate_file(config, file_path, file):
    return validate_identifiers(config, file_path, file['identifiers'])


def validate_identifiers(config, path, identifiers):
    instance = {
        'dimensions': [],
        'variables': [],
        'attributes': [],
        'identifiers': identifiers
    }

    logger.debug('instance = %s', instance)

    try:
        if config.get('resolver') is not None:
            jsonschema.validate(schema=config['schema'], resolver=config['resolver'], instance=instance)
        else:
            jsonschema.validate(schema=config['schema'], instance=instance)
    except jsonschema.exceptions.ValidationError as e:
        logger.error('instance = %s', instance)
        raise e
