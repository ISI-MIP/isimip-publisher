def gather_datasets(isimip_data_url, datasets):
    related_identifiers = []

    for dataset in datasets:
        related_identifiers.append({
            'relationType': 'HasPart',
            'relatedIdentifier': isimip_data_url + '/datasets/' + dataset.id,
            'relatedIdentifierType': 'URL'
        })

    return related_identifiers
