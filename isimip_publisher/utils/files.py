import logging
import os
import shutil
import subprocess
from pathlib import Path

from ..config import settings
from .checksum import get_checksum
from .netcdf import update_netcdf_global_attributes

logger = logging.getLogger(__name__)


def list_files(base_path, path, pattern, remote_dest=None, include=None, exclude=None):
    abs_path = base_path / path

    if remote_dest:
        args = ['ssh', remote_dest, 'find', abs_path.as_posix()]

        for suffix in pattern['suffix']:
            args += ['-name', '\'*{}\''.format(suffix)]

            if suffix != pattern['suffix'][-1]:
                args += ['-or']

    else:
        args = ['find', abs_path.as_posix()]

        for suffix in pattern['suffix']:
            args += ['-name', '*{}'.format(suffix)]

            if suffix != pattern['suffix'][-1]:
                args += ['-or']

    logger.debug('args = %s', args)

    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError:
        output = ''

    files = []
    for line in output.splitlines():
        file_abspath = line.decode()
        file_path = file_abspath.replace(base_path.as_posix() + os.sep, '')

        if include and not match_path(include, file_path):
            continue

        if exclude and match_path(exclude, file_path):
            continue

        files.append(file_path)

    return files


def match_path(path_list, file_path):
    for path in path_list:
        if path and not path.startswith('#') and file_path.startswith(path):
            return True

    return False


def copy_files(remote_dest, remote_path, local_path, path, files):
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


def move_files(source_dir, target_dir, files, keep=False):
    moves = []
    for source_path in files:
        logger.info('move_files %s', source_path)

        target_path = Path(target_dir) / Path(source_path).relative_to(source_dir)

        # check if the file is already public
        if target_path.exists():
            # raise an error if it is a different file!
            if get_checksum(source_path) != get_checksum(target_path):
                raise RuntimeError('The file %s already exists and has a different checksum than %s' %
                                   (source_path, target_path))
        else:
            moves.append((source_path, target_path))

    for source_path, target_path in moves:
        # create the directories for the file
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # copy the file
        if keep:
            logger.debug('cp %s %s', source_path, target_path)
            shutil.copy(source_path, target_path)
        else:
            logger.debug('mv %s %s', source_path, target_path)
            shutil.move(source_path, target_path)


def delete_files(local_path, path):
    abs_path = local_path / path

    logger.debug('rm -r %s', abs_path)
    try:
        shutil.rmtree(abs_path)
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
