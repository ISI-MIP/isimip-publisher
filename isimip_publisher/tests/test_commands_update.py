def test_update_datasets(setup, public_files, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_datasets', 'round/product/sector'])
    assert response.success, response.stderr
    assert 'update_datasets' in response.stdout
    assert not response.stderr
