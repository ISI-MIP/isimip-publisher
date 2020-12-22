import logging
import os
import shutil
import subprocess
from pathlib import Path

from ..config import settings
from .checksum import get_checksum, get_checksum_suffix
from .netcdf import update_netcdf_global_attributes

logger = logging.getLogger(__name__)


def list_files(base_path, path, include=None, exclude=None, remote_dest=None, suffix=None):
    abs_path = base_path / path

    if remote_dest:
        args = ['ssh', remote_dest, 'find', abs_path.as_posix(), '-type', 'f']
    else:
        args = ['find', abs_path.as_posix(), '-type', 'f']

    logger.debug('args = %s', args)

    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError:
        output = ''

    files = []
    for line in output.splitlines():
        file_abspath = line.decode()
        file_path = Path(file_abspath).relative_to(base_path)

        if file_path.suffix in [get_checksum_suffix(), '.png', '.json']:
            continue

        if suffix and file_path.suffix not in suffix:
            continue

        if include and not match_path(include, file_path):
            continue

        if exclude and match_path(exclude, file_path):
            continue

        files.append(file_path.as_posix())

    return files


def match_path(path_list, file_path):
    for path in path_list:
        if path and not path.startswith('#') and str(file_path).startswith(path):
            return True

    return False


def copy_files(remote_dest, remote_path, local_path, path, files):
    # check if path is a file
    if Path(path).suffix:
        path = Path(path).parent.as_posix()

    # create the local_dir
    abs_path = local_path / path
    if abs_path.is_dir():
        abs_path.mkdir(parents=True, exist_ok=True)
    else:
        abs_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.MOCK:
        for file in files:
            mock_path = local_path / file
            mock_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info('mock_file %s', mock_path)
            mock_file(mock_path)
            yield 1  # yield increment for the progress bar

    else:
        # write file list in temporary file
        include_file = 'rsync-include.txt'
        with open(include_file, 'w') as f:
            for file in files:
                f.write(file.replace(path, '') + os.linesep)

        source = remote_dest + ':' + (remote_path / path).as_posix() + os.path.sep
        destination = (local_path / path).as_posix() + os.path.sep
        args = [
            'rsync', '-aviL',
            '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
            source, destination
        ]
        logger.debug('args = %s', args)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # yield diff_files
        for line in process.stdout:
            output = line.decode().strip()
            if output.startswith('>f'):
                logger.info('copy_file %s', output)
                yield 1  # yield increment for the progress bar

        os.remove(include_file)


def move_file(source_path, target_path, keep=False):
    logger.info('move_file %s', source_path)

    # check if the file is already public
    if target_path.exists():
        # raise an error if it is a different file!
        if get_checksum(source_path) != get_checksum(target_path):
            raise RuntimeError('The file %s already exists and has a different checksum than %s' %
                               (source_path, target_path))

    # create the directories for the file
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # copy the file
    if keep:
        logger.debug('cp %s %s', source_path, target_path)
        shutil.copy(source_path, target_path)
    else:
        logger.debug('mv %s %s', source_path, target_path)
        shutil.move(source_path, target_path)


def delete_file(abs_path):
    logger.debug('rm %s', abs_path)
    try:
        os.remove(abs_path)
    except FileNotFoundError:
        pass


def chmod_file(file_path):
    logger.debug('chmod 644 %s', file_path)
    os.chmod(file_path, 0o644)


def mock_file(mock_path):
    if mock_path.suffix.startswith('.nc'):
        empty_file = Path(__file__).parent.parent / 'extras' / 'empty.nc'
    else:
        empty_file = Path(__file__).parent.parent / 'extras' / 'empty.txt'

    shutil.copyfile(empty_file, mock_path)

    if mock_path.suffix.startswith('.nc'):
        update_netcdf_global_attributes(mock_path, {
            'path': mock_path
        })
    else:
        mock_path.write_text('path: ' + mock_path.as_posix() + os.linesep)


def get_size(file_abspath):
    return Path(file_abspath).stat().st_size
