from . import order_dict


def get_attributes(config, obj):
    attributes = {
        'version': config['version']
    }
    attributes.update(config['attributes'])
    attributes.update(obj['identifiers'])
    return order_dict(attributes)
