import argparse

from .commands import (archive, clean, fetch, ingest, list_local, list_public,
                       list_remote, match_local, match_remote, publish,
                       update_netcdf, write_checksums, write_jsons,
                       write_thumbnails)
from .utils import setup_env, setup_logging
from .utils.config import parse_config, parse_filelist, parse_version


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path of the files to publish')
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # add a subparser for each subcommand
    subparsers.add_parser('clean').set_defaults(func=clean)
    subparsers.add_parser('archive').set_defaults(func=archive)
    subparsers.add_parser('ingest').set_defaults(func=ingest)
    subparsers.add_parser('fetch').set_defaults(func=fetch)
    subparsers.add_parser('list_remote').set_defaults(func=list_remote)
    subparsers.add_parser('list_local').set_defaults(func=list_local)
    subparsers.add_parser('list_public').set_defaults(func=list_public)
    subparsers.add_parser('match_local').set_defaults(func=match_local)
    subparsers.add_parser('match_remote').set_defaults(func=match_remote)
    subparsers.add_parser('publish').set_defaults(func=publish)
    subparsers.add_parser('update_netcdf').set_defaults(func=update_netcdf)
    subparsers.add_parser('write_checksums').set_defaults(func=write_checksums)
    subparsers.add_parser('write_jsons').set_defaults(func=write_jsons)
    subparsers.add_parser('write_thumbnails').set_defaults(func=write_thumbnails)

    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('run_all').set_defaults(func=run_all)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        version = parse_version(args.version)
        config = parse_config(args.path, version)
        filelist = parse_filelist(args.filelist_file)

        if config is False:
            parser.error('path needs to contain at least 3 tokens')

        args.func(version, config, filelist)
    else:
        parser.print_help()


def run(version, config, filelist=None):
    clean(version, config, filelist)
    match_remote(version, config, filelist)
    fetch(version, config, filelist)
    update_netcdf(version, config, filelist)
    write_checksums(version, config, filelist)
    write_jsons(version, config, filelist)
    write_thumbnails(version, config, filelist)
    ingest(version, config, filelist)
    publish(version, config, filelist)


def run_all(version, config, filelist=None):
    clean(version, config, filelist)
    list_remote(version, config, filelist)
    match_remote(version, config, filelist)
    fetch(version, config, filelist)
    list_local(version, config, filelist)
    match_local(version, config, filelist)
    update_netcdf(version, config, filelist)
    write_checksums(version, config, filelist)
    write_jsons(version, config, filelist)
    write_thumbnails(version, config, filelist)
    ingest(version, config, filelist)
    publish(version, config, filelist)
    archive(version, config, filelist)
