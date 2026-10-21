def test_empty(setup, script_runner):
    response = script_runner.run(['isimip-publisher'])
    assert not response.stderr
    assert response.returncode == 0


def test_help(setup, script_runner):
    response = script_runner.run(['isimip-publisher', '--help'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_check(setup, public_files, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'check', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_tree(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_tree', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_search(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_search', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_views(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_views'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_clean(setup, script_runner):
    response = script_runner.run(['isimip-publisher', 'clean', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_init(setup, db, script_runner):
    response = script_runner.run(['isimip-publisher', 'init'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
