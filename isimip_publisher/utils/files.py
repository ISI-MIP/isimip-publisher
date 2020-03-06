import logging
import os
import shutil
import subprocess
from pathlib import Path

from .checksum import get_checksum

logger = logging.getLogger(__name__)


def list_files(config, base_path, remote_dest=None, filelist=None):
    path = base_path / config['path']

    if remote_dest:
        args = ['ssh', remote_dest, 'find', path, '-name', '\'*.nc*\'']
    else:
        args = ['find', path, '-name', '*.nc*']

    output = subprocess.check_output(args)

    files = []
    for line in output.splitlines():
        file_abspath = line.decode()
        file_path = file_abspath.replace(str(base_path) + os.sep, '')
        if not filelist or file_path in filelist:
            files.append(file_path)

    logger.debug(files)
    return files


def copy_files(config, remote_dest, remote_path, local_path, files):
    mock = os.environ.get('MOCK').lower() in ['t', 'true', 1]

    # create the local_dir
    (local_path / config['path']).mkdir(parents=True, exist_ok=True)

    if mock:
        empty_file = Path(__file__).parent.parent / 'extras' / 'empty.nc'

        for file in files:
            mock_path = local_path / file
            mock_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(empty_file, mock_path)
            yield 1  # yield increment for the progress bar

    else:
        # write file list in temporary file
        include_file = 'rsync-include.txt'
        with open(include_file, 'w') as f:
            for file in files:
                f.write(file.replace(config['path'], '') + os.linesep)

        source = remote_dest + ':' + str(remote_path / config['path']) + os.path.sep
        destination = str(local_path / config['path']) + os.path.sep
        args = [
            'rsync', '-azvi',
            '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
            source, destination
        ]
        logger.debug('args = %s', args)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # yield diff_files
        for line in process.stdout:
            output = line.decode().strip()
            if output.startswith('>f'):
                logger.info('rsync %s', output)
                yield 1  # yield increment for the progress bar

        os.remove(include_file)


def move_files(source_dir, target_dir, files):
    moves = []
    for source_path in files:
        target_path = Path(str(source_path).replace(str(source_dir), str(target_dir)))

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
        logger.info('mv %s %s', source_path, target_path)
        shutil.move(source_path, target_path)


def delete_files(config):
    local_path = Path(os.environ['LOCAL_DIR'] % config)
    logger.info('rm -r %s', local_path)
    try:
        shutil.rmtree(local_path)
    except FileNotFoundError:
        pass


def chmod_file(file_path):
    logger.info('chmod 644 %s', file_path)
    os.chmod(file_path, 0o644)
