from pathlib import Path


def validate_datasets(schema, datasets):
    for dataset in datasets:
        dataset.validate(schema)

        for file in dataset.files:
            file.validate(schema)

            # file_path = Path(file.abspath)
            # assert file_path.is_file(), '{} does not exist'.format(file_path)
            # for suffix in ['.json', '.png']:
            #     assert file_path.with_suffix(suffix).is_file(), '{} does not exist'.format(file_path.with_suffix(suffix))
