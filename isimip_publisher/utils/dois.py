from datacite import DataCiteMDSClient, schema43


def get_doi(datacite):
    return next(item.get('identifier')
                for item in datacite.get('identifiers', [])
                if item.get('identifierType') == 'DOI')


def get_title(datacite):
    return next(item.get('title')
                for item in datacite.get('titles', []))


def upload_doi(resource, isimip_data_url,
               datacite_username, datacite_password, datacite_prefix, datacite_test_mode):
    # get the doi and the url
    doi = get_doi(resource.datacite)
    url = '{base}/{doi}'.format(base=isimip_data_url, doi=doi)

    # convert the metadata to xml
    xml = schema43.tostring(resource.datacite)

    # get the mds client
    mds_client = DataCiteMDSClient(
        username=datacite_username,
        password=datacite_password,
        prefix=datacite_prefix,
        test_mode=datacite_test_mode
    )

    # upload the metadata
    mds_metadata_response = mds_client.metadata_post(xml)
    print(mds_metadata_response)

    # register the doi
    mds_doi_response = mds_client.doi_post(doi, url)
    print(mds_doi_response)
