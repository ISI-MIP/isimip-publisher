def test_diff_remote(setup, remote_files, empty_public, script_runner):
    response = script_runner.run(['isimip-publisher', 'diff_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_diff_remote_public(setup, remote_files, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'diff_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_diff_remote_links(setup, remote_links, empty_public, script_runner):
    response = script_runner.run(['isimip-publisher', 'diff_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_diff_remote_links_public(setup, remote_links, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'diff_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
