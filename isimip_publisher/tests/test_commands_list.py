def test_list_remote(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_remote2(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 0


def test_list_remote_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_local(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_local', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_public(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_public', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_public_links(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_public_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6
