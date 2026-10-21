import os
import shutil
from pathlib import Path


def test_publish_datasets(setup, local_files, db, local_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'publish_datasets', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_publish_datasets_amend_replace(
    setup,
    local_files,
    public_files,
    empty_archive,
    db,
    public_datasets,
    empty_store,
    amend_file,
    script_runner,
):
    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'insert_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'publish_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_publish_datasets_amend_add(
    setup,
    local_files,
    public_files,
    empty_archive,
    db,
    public_datasets,
    empty_store,
    amend_file,
    script_runner,
):
    local_path = Path(os.getenv('ISIMIP_LOCAL_DIR')) / 'round/product/sector/model'

    # add a new file to the ipsum dataset
    shutil.copyfile(
        local_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2002_2003.nc',
        local_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2003_2004.nc',
    )

    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2003_2004.nc')

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'write_local_jsons', 'round/product/sector']
    )
    assert response.success, response.stderr

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'insert_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'publish_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_publish_datasets_amend_twice(
    setup,
    local_files,
    public_files,
    empty_archive,
    db,
    public_datasets,
    empty_store,
    amend_file,
    script_runner,
):
    local_path = Path(os.getenv('ISIMIP_LOCAL_DIR')) / 'round/product/sector/model'
    public_path = Path(os.getenv('ISIMIP_PUBLIC_DIR')) / 'round/product/sector/model'

    amend = amend_file('round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc')

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'insert_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240101', 'publish_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr

    # amend the same file again with a later version
    shutil.copyfile(
        public_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc',
        local_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc',
    )
    shutil.copyfile(
        public_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.json',
        local_path / 'model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.json',
    )

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240201', 'insert_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr

    response = script_runner.run(
        ['isimip-publisher', '--amend', amend, '-v', '20240201', 'publish_datasets', 'round/product/sector']
    )
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')
