from . import order_dict

def get_netcdf_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['netcdf_metadata'])


def get_dataset_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['dataset_metadata'])


def get_file_metadata(config, identifiers):
    return get_metadata(config, identifiers, config['file_metadata'])


def get_metadata(config, identifiers, metadata_keys):
    # get everything from config which is a str
    values = {key: value for key, value in config.items() if isinstance(value, str)}

    # add identifiers
    values.update(identifiers)

    # add everything from model config which is a str
    model_config = config['models'].get(config['model'], {}) or {}
    model_values = {key: value for key, value in model_config.items() if isinstance(value, str)}
    values.update(model_values)

    # return values for keys or templates
    metadata = {}
    for key in metadata_keys:
        template_key = '%s_template' % key
        if key in values:
            metadata[key] = values[key]
        elif template_key in values:
            metadata[key] = values[template_key] % values

    # order metadata and return
    return order_dict(metadata)
