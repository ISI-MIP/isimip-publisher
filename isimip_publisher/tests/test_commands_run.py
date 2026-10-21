def test_run(setup, remote_files, empty_local, empty_public, db, empty_store, script_runner):
    response = script_runner.run(['isimip-publisher', 'run', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout


def test_run_amend(setup, remote_files, empty_local, public_files, empty_archive, db, public_datasets,
                   empty_store, amend_file, script_runner):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(['isimip-publisher', '--amend', amend, '-v', '20240101',
                                  'run', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
