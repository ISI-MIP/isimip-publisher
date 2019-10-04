import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)


def list_remote_files(config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.path.join(os.environ['REMOTE_DIR'] % config, '')
    return find_files(['ssh', remote_dest, 'find', remote_dir, '-type', 'f', '-name', '*.nc4'], filelist)


def list_local_files(config, filelist=None):
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')
    return find_files(['find', local_dir, '-type', 'f', '-name', '*.nc4'], filelist)


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
    remote_dir = os.path.join(os.environ['REMOTE_DIR'] % config, '')
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')

    yield from rsync_files(remote_dest + ':' + remote_dir, local_dir, [file.replace(remote_dir, '') for file in files])


def rsync_files_to_public(config, files):
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')
    public_dir = os.path.join(os.environ['PUBLIC_DIR'] % config, '')

    yield from rsync_files(local_dir, public_dir, [file.replace(local_dir, '') for file in files])


def rsync_files(source, destination, files):
    os.makedirs(destination, exist_ok=True)

    # write file list in temporary file
    include_file = 'rsync-include.txt'
    with open(include_file, 'w') as f:
        for file in files:
            f.write(file.replace(source, '') + os.linesep)

    # make a dry-run to get the number of files to transfer
    output = subprocess.check_output([
        'rsync', '-avz', '--stats', '--dry-run', '--include=*/', '--include-from=%s' % include_file, '--exclude=*', source, destination
    ])

    # get the total number of files from the output of rsync
    match = re.findall(r'Number of regular files transferred: (\d{1,3}(,\d{3})*)', output.decode())
    total_files = int(match[0][0].replace(',', ''))

    # get the number of files which were already transfered
    diff_files = len(files) - total_files

    process = subprocess.Popen([
        'rsync', '-azvi', '--include=*/', '--include-from=%s' % include_file, '--exclude=*', source, destination
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    yield diff_files
    for line in process.stdout:
        output = line.decode().strip()
        if output.startswith('>f'):
            logger.debug('rsync %s', output)
            yield 1

    os.remove(include_file)


def chmod_file(file_path):
    logger.debug('chmod 644 %s', file_path)
    os.chmod(file_path, 0o644)


def delete_file(file_path):
    logger.debug('rm %s', file_path)
    os.remove(file_path)


def rename_file(file_path, new_file_path):
    logger.debug('mv %s %s', file_path, new_file_path)
    os.rename(file_path, new_file_path)
