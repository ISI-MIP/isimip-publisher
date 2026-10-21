def test_archive_datasets_yes(setup, db, mocker, public_datasets, script_runner):
    mocker.patch('builtins.input', return_value='yes')

    response = script_runner.run(['isimip-publisher', 'archive_datasets', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert response.stdout.strip().startswith('Archiving')
    assert response.stderr.strip().startswith('archive_datasets')


def test_archive_datasets_no(setup, db, mocker, public_datasets, script_runner):
    mocker.patch('builtins.input', return_value='no')

    response = script_runner.run(['isimip-publisher', 'archive_datasets', 'round/product/sector/model'])
    assert response.success
    assert response.stdout.strip().startswith('Archiving')
    assert not response.stderr
