def test_write_local_jsons(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'write_local_jsons', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_local_jsons')


def test_write_local_jsons_amend(setup, local_files, empty_store, amend_file, script_runner):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(['isimip-publisher', '--amend', amend, 'write_local_jsons', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_local_jsons')


def test_write_public_jsons(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'write_public_jsons', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_public_jsons')


def test_write_link_jsons(setup, public_links, script_runner):
    response = script_runner.run(
        ['isimip-publisher', 'write_link_jsons', 'round/product/sector/model', 'round/product/sector2/model']
    )
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_link_jsons')
