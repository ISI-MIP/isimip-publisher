import json as python_json

from . import order_dict


def write_json(config, metadata, file):
    with open(file.replace('.nc4', '.json'), 'w') as f:
        f.write(python_json.dumps(order_dict(metadata), indent=2))
