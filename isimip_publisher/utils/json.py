import json as python_json

from isimip_publisher.utils import order_dict


def write_json(config, metadata, file):
    # filter metadata according to config
    metadata = order_dict({key: value for key, value in metadata.items() if key in list(config['json_metadata'])})

    with open(file.replace('.nc4', '.json'), 'w') as f:
        f.write(python_json.dumps(metadata, indent=2))
