def get_netcdf_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['netcdf_metadata'])


def get_json_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['json_metadata'])


def get_database_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['database_metadata'])


def get_metadata(config, identifiers, filter_list=None):

    # get everything from config which is a str
    metadata = {key: value for key, value in config.items() if isinstance(value, str)}

    # add identifiers
    metadata.update(identifiers)

    # add everything from model config which is a str
    model_config = config['models'].get(config['model'], {}) or {}
    model_metadata = {key: value for key, value in model_config.items() if isinstance(value, str)}
    metadata.update(model_metadata)

    # add template metadata
    templates = {}
    for key, template in config['templates'].items():
        templates[key] = template % metadata
    metadata.update(templates)

    # return everyting or filter
    if filter_list:
        return {key: value for key, value in metadata.items() if key in filter_list}
    else:
        return metadata
