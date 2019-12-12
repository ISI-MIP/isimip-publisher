import json as python_json


def write_dataset_json(config, dataset_path, metadata):
    with open('%s.json' % dataset_path, 'w') as f:
        f.write(python_json.dumps(metadata, indent=2))


def write_file_json(config, file_path, metadata):
    with open(file_path.replace('.nc4', '.json'), 'w') as f:
        f.write(python_json.dumps(metadata, indent=2))
