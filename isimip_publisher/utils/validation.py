def validate_dataset(config, dataset_path, dataset):
    return validate_identifiers(config, dataset_path, dataset['identifiers'])


def validate_file(config, file_path, file):
    return validate_identifiers(config, file_path, file['identifiers'])


def validate_identifiers(config, path, identifiers):
    for key, value in identifiers.items():

        if key == 'model':
            assert value in config['models'], \
                'Model %s is not configured.' % value

        elif key == 'modelname':
            assert (value == identifiers['model'].lower()
                    or value == config['models'].get(identifiers['model']).get('modelname')), \
                'Modelname %s is not configured.' % value

        else:
            validation_key = '%s_validation' % key

            if validation_key in config:
                values = config[validation_key]

                assert value in values, \
                    "%s mismatch: '%s' not in %s for %s" % \
                    (key, value, values, path)
