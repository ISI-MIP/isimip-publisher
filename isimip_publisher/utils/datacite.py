def gather_related_identifiers(datacite, isimip_data_url, datasets):
    if 'relatedIdentifiers' not in datacite:
        datacite['relatedIdentifiers'] = []

    for dataset in datasets:
        datacite['relatedIdentifiers'].append({
            'relationType': 'HasPart',
            'relatedIdentifier': isimip_data_url + '/datasets/' + dataset.id,
            'relatedIdentifierType': 'URL'
        })
