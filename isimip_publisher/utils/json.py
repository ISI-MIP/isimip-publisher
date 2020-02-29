import json as python_json


def write_file_json(config, file, attributes):
    json_path = file['abspath'].with_suffix('.json')
    with open(json_path, 'w') as f:
        f.write(python_json.dumps(attributes, indent=2))
