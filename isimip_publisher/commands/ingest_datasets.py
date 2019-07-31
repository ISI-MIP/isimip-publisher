from isimip_publisher.database.utils import init_database_session, insert_dataset

from isimip_publisher.utils import get_subparser_title
from isimip_publisher.utils.config import parse_config, parse_filelist, parse_version
from isimip_publisher.utils.datasets import find_datasets
from isimip_publisher.utils.files import list_local_files


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')
    parser.set_defaults(func=main)


def main(args):
    version = parse_version(args.version)
    config = parse_config(args.simulation_round, args.sector, args.model, version)
    filelist = parse_filelist(args.filelist_file)
    files = list_local_files(config, filelist)
    datasets = find_datasets(config, files)

    session = init_database_session()

    for dataset in datasets:
        insert_dataset(session, dataset, {}, version)

    session.commit()
