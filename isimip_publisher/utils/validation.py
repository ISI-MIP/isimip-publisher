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
