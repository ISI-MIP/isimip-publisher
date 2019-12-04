import logging
import os
import re
import shutil
import subprocess

from . import add_version_to_path
from .checksum import get_checksum

logger = logging.getLogger(__name__)


def list_remote_files(config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.path.join(os.environ['REMOTE_DIR'], config['path'])
    return find_files(['ssh', remote_dest, 'find', remote_dir.rstrip('/'), '-type', 'f', '-name', '\'*.nc4\''], filelist)


def list_local_files(config, filelist=None):
    local_dir = os.path.join(os.environ['LOCAL_DIR'], config['path'])
    return find_files(['find', local_dir.rstrip('/'), '-type', 'f', '-name', '*.nc4'], filelist)


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


def copy_files_from_remote(config, files):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.path.join(os.environ['REMOTE_DIR'], config['path'], '')
    local_dir = os.path.join(os.environ['LOCAL_DIR'], config['path'], '')

    if os.path.exists(local_dir):
        raise RuntimeError('LOCAL_DIR already exists, run "clean" first!')

    # create the local_dir
    os.makedirs(local_dir, exist_ok=True)

    # write file list in temporary file
    include_file = 'rsync-include.txt'
    with open(include_file, 'w') as f:
        for file in files:
            f.write(file.replace(remote_dir, '') + os.linesep)

    # make a dry-run to get the number of files to transfer
    output = subprocess.check_output([
        'rsync', '-avz', '--stats', '--dry-run',
        '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
        remote_dest + ':' + remote_dir, local_dir
    ])

    # get the total number of files from the output of rsync
    match = re.findall(r'transferred: (\d{1,3}(,\d{3})*)', output.decode())
    total_files = int(match[0][0].replace(',', ''))

    # get the number of files which were already transfered
    diff_files = len(files) - total_files

    process = subprocess.Popen([
        'rsync', '-azvi',
        '--include=*/', '--include-from=%s' % include_file, '--exclude=*',
        remote_dest + ':' + remote_dir, local_dir
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    yield diff_files
    for line in process.stdout:
        output = line.decode().strip()
        if output.startswith('>f'):
            logger.info('rsync %s', output)
            yield 1  # yield increment for the progress bar

    os.remove(include_file)


def copy_files_to_public(version, config, files):
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')
    public_dir = os.path.join(os.environ['PUBLIC_DIR'] % config, '')

    copy_files = []
    for file_path in files:
        version_path = add_version_to_path(file_path, version)
        target_path = version_path.replace(local_dir, public_dir)

        # check if the file is already public
        if os.path.exists(target_path):
            # raise an error it it is a different file!
            if get_checksum(file_path) != get_checksum(target_path):
                raise RuntimeError('The file %s already exists and has a different checksum than %s' % (file_path, target_path))
        else:
            copy_files.append((file_path, target_path))

    yield len(files) - len(copy_files)
    for file_path, target_path in copy_files:
        # create the directories for the file
        target_dir = os.path.dirname(target_path)
        logger.info('mkdir -p %s', target_dir)
        os.makedirs(target_dir, exist_ok=True)

        # copy the file
        logger.info('cp %s %s', file_path, target_path)
        shutil.copyfile(file_path, target_path)

        yield 1  # yield increment for the progress bar


def delete_files(config):
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')
    logger.info('rm -r %s', local_dir)
    try:
        shutil.rmtree(local_dir)
    except FileNotFoundError:
        pass


def chmod_file(file_path):
    logger.info('chmod 644 %s', file_path)
    os.chmod(file_path, 0o644)
