import logging

import jsonschema

logger = logging.getLogger(__name__)


def validate_dataset(config, dataset):
    return validate_identifiers(config, dataset['identifiers'])


def validate_file(config, file):
    return validate_identifiers(config, file['identifiers'])


def validate_identifiers(config, identifiers):
    logger.debug('identifiers = %s', identifiers)

    try:
        jsonschema.validate(schema=config['schema'], instance=identifiers)
    except jsonschema.exceptions.ValidationError as e:
        logger.error('identifiers = %s', identifiers)
        raise e
