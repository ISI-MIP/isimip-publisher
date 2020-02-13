import logging
import os
import re
import shutil
import subprocess

from .checksum import get_checksum

logger = logging.getLogger(__name__)


def list_remote_files(config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_dir = os.path.join(os.environ['REMOTE_DIR'], config['path'])
    return find_files(['ssh', remote_dest, 'find', remote_dir.rstrip('/'), '-name', '\'*.nc4\''], filelist)


def list_local_files(config, filelist=None):
    local_dir = os.path.join(os.environ['LOCAL_DIR'], config['path'])
    return find_files(['find', local_dir.rstrip('/'), '-name', '*.nc4'], filelist)


def list_public_files(config, filelist=None):
    public_dir = os.path.join(os.environ['PUBLIC_DIR'], config['path'])
    return find_files(['find', public_dir.rstrip('/'), '-name', '*.nc4'], filelist)


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
    remote_dir = os.path.join(os.environ['REMOTE_DIR'], config['path'], '')
    local_dir = os.path.join(os.environ['LOCAL_DIR'], config['path'], '')
    mock = os.environ.get('MOCK', '').lower() in ['t', 'true', 1]

    if os.path.exists(local_dir):
        raise RuntimeError('LOCAL_DIR already exists, run "clean" first!')

    # create the local_dir
    os.makedirs(local_dir, exist_ok=True)

    if mock:
        empty_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'extras', 'empty.nc4')

        for file in files:
            mock_path = file.replace(remote_dir, local_dir)
            mock_dir = os.path.dirname(mock_path)

            os.makedirs(mock_dir, exist_ok=True)
            shutil.copyfile(empty_file, mock_path)
            yield 1  # yield increment for the progress bar

    else:
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


def move_files_to_public(config, files):
    local_dir = os.path.join(os.environ['LOCAL_DIR'] % config, '')
    public_dir = os.path.join(os.environ['PUBLIC_DIR'] % config, '')
    move_files(local_dir, public_dir, files)


def move_files_to_archive(config, version, files):
    public_dir = os.path.join(os.environ['PUBLIC_DIR'] % config, '')
    archive_dir = os.path.join(os.environ['ARCHIVE_DIR'] % config, version, '')
    move_files(public_dir, archive_dir, files)


def move_files(source_dir, target_dir, files):
    moves = []
    for source_path in files:
        target_path = source_path.replace(source_dir, target_dir)

        # check if the file is already public
        if os.path.exists(target_path):
            # raise an error if it is a different file!
            if get_checksum(source_path) != get_checksum(target_path):
                raise RuntimeError('The file %s already exists and has a different checksum than %s' %
                                   (source_path, target_path))
        else:
            moves.append((source_path, target_path))

    for source_path, target_path in moves:
        # create the directories for the file
        target_dir = os.path.dirname(target_path)
        logger.info('mkdir -p %s', target_dir)
        os.makedirs(target_dir, exist_ok=True)

        # copy the file
        logger.info('mv %s %s', source_path, target_path)
        shutil.move(source_path, target_path)


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
