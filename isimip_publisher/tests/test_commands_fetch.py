def test_fetch_files(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'fetch_files', 'round/product/sector'])
    assert response.success, response.stderr
    assert 'fetch_files' in response.stdout
    assert not response.stderr


def test_fetch_files_amend(setup, remote_files, empty_local, amend_file, script_runner):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(['isimip-publisher', '--amend', amend, 'fetch_files', 'round/product/sector'])
    assert response.success, response.stderr
    assert 'fetch_files' in response.stdout
    assert not response.stderr
