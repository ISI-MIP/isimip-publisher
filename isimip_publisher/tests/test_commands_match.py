def test_match_remote(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote_amend(setup, remote_files, amend_file, script_runner):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(['isimip-publisher', '--amend', amend, 'match_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 1


def test_match_remote_amend_missing(setup, remote_files, amend_file, script_runner):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2003_2004.nc')

    response = script_runner.run(['isimip-publisher', '--amend', amend, 'match_remote', 'round/product/sector'])
    assert not response.success


def test_match_local(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_local', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_public(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_public', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_public_links(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_public_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6
