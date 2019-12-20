from . import order_dict


def get_attributes(config, identifiers):
    attributes = config['attributes']
    attributes.update(identifiers)
    return order_dict(attributes)
