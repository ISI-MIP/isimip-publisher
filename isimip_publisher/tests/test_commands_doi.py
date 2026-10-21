def test_insert_doi(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', '--skip-registration', 'insert_doi',
                                  'testing/resources/test.json', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_doi(setup, db, public_datasets, resources, script_runner):
    response = script_runner.run(['isimip-publisher', '--skip-registration', 'update_doi',
                                  'testing/resources/test1.json'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_check_doi(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'check_doi', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_check_doi_with_resources(setup, db, public_datasets, resources, script_runner):
    response = script_runner.run(['isimip-publisher', 'check_doi', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_register_doi_yes(setup, db, mocker, public_datasets, resources, script_runner):
    mocker.patch('builtins.input', return_value='yes')
    upload_doi = mocker.patch('isimip_publisher.utils.dois.upload_doi')

    response = script_runner.run(['isimip-publisher', 'register_doi', '10.12345/ISIMIP.001'])
    assert response.success, response.stderr
    assert response.stdout.strip().startswith('Registering')
    assert not response.stderr
    upload_doi.assert_called_once()


def test_register_doi_no(setup, db, mocker, public_datasets, resources, script_runner):
    mocker.patch('builtins.input', return_value='no')
    upload_doi = mocker.patch('isimip_publisher.utils.dois.upload_doi')

    response = script_runner.run(['isimip-publisher', 'register_doi', '10.12345/ISIMIP.001'])
    assert response.success, response.stderr
    assert response.stdout.strip().startswith('Registering')
    assert not response.stderr
    upload_doi.assert_not_called()
