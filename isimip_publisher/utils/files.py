import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

from .checksum import get_checksum

logger = logging.getLogger(__name__)


def list_remote_files(config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR']) / config['path']
    return find_files(['ssh', remote_dest, 'find', remote_path, '-name', '\'*.nc*\''], filelist)


def list_local_files(config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR']) / config['path']
    return find_files(['find', local_path, '-name', '*.nc*'], filelist)


def list_public_files(config, filelist=None):
    public_path = Path(os.environ['PUBLIC_DIR']) / config['path']
    return find_files(['find', public_path, '-name', '*.nc*'], filelist)


def find_files(args, filelist=None):
    output = subprocess.check_output(args)

    files = []
    for line in output.splitlines():
        file_abspath = line.decode()
        if filelist:
            if file_abspath in filelist:
                files.append(file_abspath)
        else:
            files.append(file_abspath)

    logger.debug(files)
    return files


def rsync_files_from_remote(config, files):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR']) / config['path']
    local_path = Path(os.environ['LOCAL_DIR']) / config['path']
    mock = os.environ.get('MOCK', '').lower() in ['t', 'true', 1]

    if local_path.exists():
        raise RuntimeError('LOCAL_DIR already exists, run "clean" first!')

    # create the local_dir
    local_path.mkdir(parents=True, exist_ok=True)

    if mock:
        empty_file = Path(__file__).parent.parent / 'extras' / 'empty.nc'

        for file in files:
            mock_path = Path(file.replace(str(remote_path), str(local_path)))
            mock_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(empty_file, mock_path)
            yield 1  # yield increment for the progress bar

    else:
        # write file list in temporary file
        include_file = 'rsync-include.txt'
        with open(include_file, 'w') as f:
            for file in files:
                f.write(file.replace(str(remote_path) + os.sep, '') + os.linesep)

        # make a dry-run to get the number of files to transfer
        output = subprocess.check_output([
            'rsync', '-avz', '--stats', '--dry-run',
            '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
            remote_dest + ':' + str(remote_path), str(local_path)
        ])

        # get the total number of files from the output of rsync
        match = re.findall(r'transferred: (\d{1,3}(,\d{3})*)', output.decode())
        total_files = int(match[0][0].replace(',', ''))

        # get the number of files which were already transfered
        diff_files = len(files) - total_files

        process = subprocess.Popen([
            'rsync', '-azvi',
            '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
            remote_dest + ':' + str(remote_path), str(local_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        yield diff_files
        for line in process.stdout:
            output = line.decode().strip()
            if output.startswith('>f'):
                logger.info('rsync %s', output)
                yield 1  # yield increment for the progress bar

        os.remove(include_file)


def move_files_to_public(config, files):
    local_path = Path(os.environ['LOCAL_DIR'] % config)
    public_path = Path(os.environ['PUBLIC_DIR'] % config)
    move_files(local_path, public_path, files)


def move_files_to_archive(config, version, files):
    public_path = Path(os.environ['PUBLIC_DIR'] % config)
    archive_path = Path(os.environ['ARCHIVE_DIR'] % config) / version
    move_files(public_path, archive_path, files)


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
