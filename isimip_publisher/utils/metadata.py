def get_metadata(config, identifiers):
    # get everything from config which is a str
    metadata = {key: value for key, value in config.items() if isinstance(value, str)}

    # add identifiers
    metadata.update(identifiers)

    # add model metadata
    model_config = config['models'].get(config['model'].lower(), {}) or {}
    model_metadata = model_config.get('metadata', {}) or {}
    metadata.update(model_metadata)

    # add templated metadata
    templates = {}
    for key, template in config['templates'].items():
        templates[key] = template % metadata

    metadata.update(templates)
    return metadata
