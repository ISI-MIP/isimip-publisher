def test_link(setup, remote_links, public_links, db, public_datasets, script_runner):
    response = script_runner.run(
        ['isimip-publisher', 'link', 'round/product/sector/model', 'round/product/sector2/model']
    )
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_link_links(setup, remote_links, script_runner):
    response = script_runner.run(
        ['isimip-publisher', 'link_links', 'round/product/sector/model', 'round/product/sector2/model']
    )
    assert response.success, response.stderr
    assert 'link_links' in response.stdout
    assert not response.stderr


def test_link_files(setup, remote_files, script_runner):
    response = script_runner.run(
        ['isimip-publisher', 'link_files', 'round/product/sector/model', 'round/product/sector2/model']
    )
    assert response.success, response.stderr
    assert 'link_files' in response.stdout
    assert not response.stderr


def test_link_datasets(setup, db, public_datasets, public_links, script_runner):
    response = script_runner.run(
        ['isimip-publisher', 'link_datasets', 'round/product/sector/model', 'round/product/sector2/model']
    )
    assert response.success, response.stderr
    assert 'link_datasets' in response.stdout
    assert not response.stderr
