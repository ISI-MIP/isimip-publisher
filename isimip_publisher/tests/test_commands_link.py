def test_link(setup, remote_links, public_links, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'link',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout


def test_link_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_links',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_links')


def test_link_files(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_files',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_files')


def test_link_datasets(setup, db, public_datasets, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_datasets',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_datasets')
