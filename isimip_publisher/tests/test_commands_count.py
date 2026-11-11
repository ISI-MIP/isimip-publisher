def test_count_remote(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'count_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert response.stdout.strip() == '6'


def test_count_remote_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'count_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert response.stdout.strip() == '6'


def test_count_local(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'count_local', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert response.stdout.strip() == '6'


def test_count_public(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'count_public', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert response.stdout.strip() == '6'


def test_count_public_links(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'count_public_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert response.stdout.strip() == '6'
