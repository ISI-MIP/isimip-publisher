import requests


def get_doi(datacite):
    return next(item.get('identifier')
                for item in datacite.get('identifiers', [])
                if item.get('identifierType') == 'DOI')


def add_datasets_to_related_identifiers(datasets, datacite, isimip_data_url):
    if 'relatedIdentifiers' not in datacite:
        datacite['relatedIdentifiers'] = []

    for dataset in datasets:
        datacite['relatedIdentifiers'].append({
            'relationType': 'HasPart',
            'relatedIdentifier': isimip_data_url + '/datasets/' + dataset.id,
            'relatedIdentifierType': 'URL'
        })

    return datacite


def fetch_datacite_xml(isimip_data_url, doi):
    xml_url = '{base}/{doi}.datacite.xml'.format(base=isimip_data_url, doi=doi)
    xml_response = requests.get(xml_url)
    xml_response.raise_for_status()
    return xml_response.content


def upload_doi_metadata(doi, xml, datacite_metadata_url, datacite_username, datacite_password):
    metadata_url = '{base}/{doi}'.format(base=datacite_metadata_url, doi=doi)
    metadata_response = requests.put(metadata_url, xml, auth=(datacite_username, datacite_password))
    metadata_response.raise_for_status()
    print(metadata_response.content.decode())


def upload_doi(isimip_data_url, doi, datacite_doi_url, datacite_username, datacite_password):
    doi_string = 'doi={doi}\nurl={base}/{doi}'.format(base=isimip_data_url, doi=doi)
    doi_url = '{base}/{doi}'.format(base=datacite_doi_url, doi=doi)
    doi_response = requests.put(doi_url, doi_string, auth=(datacite_username, datacite_password))
    doi_response.raise_for_status()
    print(doi_response.content.decode())
