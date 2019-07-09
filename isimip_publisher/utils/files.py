import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def list_remote_files(config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.environ['REMOTE_DIR'] % config

    output = subprocess.check_output([
        'ssh', remote_dest, 'find', remote_dir, '-type', 'f', '-name', '*.nc4'])

    files = []
    for line in output.splitlines():
        file = line.decode()
        if filelist:
            if file.replace(remote_dir, '') in filelist:
                files.append(file)
        else:
            files.append(file)

    logger.debug(files)
    return files


def list_local_files(config, filelist=None):
    local_dir = os.environ['TMP_DIR'] % config

    output = subprocess.check_output([
        'find', local_dir, '-type', 'f', '-name', '*.nc4'])

    files = []
    for line in output.splitlines():
        file = line.decode()
        if filelist:
            if file.replace(local_dir, '') in filelist:
                files.append(file)
        else:
            files.append(file)

    logger.debug(files)
    return files


def copy_files(config, files):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.path.join(os.environ['REMOTE_DIR'] % config, '')
    local_dir = os.path.join(os.environ['TMP_DIR'] % config, '')

    return rsync_files(remote_dest + ':' + remote_dir, local_dir, [file.replace(remote_dir, '') for file in files])


def publish_files(config, files):
    tmp_dir = os.path.join(os.environ['TMP_DIR'] % config, '')
    pub_dir = os.path.join(os.environ['PUB_DIR'] % config, '')

    return rsync_files(tmp_dir, pub_dir, [file.replace(tmp_dir, '') for file in files])


def rsync_files(source, destination, files):
    os.makedirs(destination, exist_ok=True)

    # write file list in temporary file
    include_file = 'rsync-include.txt'
    with open(include_file, 'w') as f:
        for file in files:
            f.write(file.replace(source, '') + os.linesep)

    p = subprocess.Popen([
        'rsync', '-av', '--include=*/', '--include-from=%s' % include_file, '--exclude=*', source, destination
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in p.stdout:
        logger.debug('copy %s', line.decode().strip())

    os.remove(include_file)

    return [destination + file for file in files]


def chmod_files(files):
    for file_path in files:
        logger.debug('chmod 644 %s', file_path)
        os.chmod(file_path, 0o644)


def delete_files(files):
    for file_path in files:
        logger.debug('rm %s', file_path)
        os.remove(file_path)
